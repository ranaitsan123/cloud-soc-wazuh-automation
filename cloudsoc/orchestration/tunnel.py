from __future__ import annotations

import json
import os
import signal
import socket
import ssl
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cloudsoc.models.tunnel import TunnelSessionData
from cloudsoc.services.tunnel_state import TunnelStateStore


@dataclass
class TunnelSession:
    instance_id: str
    session_id: str
    local_port: int
    remote_port: int
    process: Optional[subprocess.Popen]
    started_at: float
    local_address: str = "127.0.0.1"
    pid: Optional[int] = None

    def to_data(self) -> TunnelSessionData:
        return TunnelSessionData(
            instance_id=self.instance_id,
            session_id=self.session_id,
            local_port=self.local_port,
            remote_port=self.remote_port,
            started_at=self.started_at,
            local_address=self.local_address,
            pid=self.pid,
        )

    @classmethod
    def from_data(cls, data: TunnelSessionData) -> "TunnelSession":
        return cls(
            instance_id=data.instance_id,
            session_id=data.session_id,
            local_port=data.local_port,
            remote_port=data.remote_port,
            process=None,
            started_at=data.started_at,
            local_address=data.local_address,
            pid=data.pid,
        )


class SSMDashboardTunnelManager:
    def __init__(self) -> None:
        self.active_session: Optional[TunnelSession] = None
        self.state_store = TunnelStateStore()

    def _save_state(self) -> None:
        if not self.active_session:
            self.state_store.remove()
            return
        self.state_store.save(self.active_session.to_data())

    def _remove_state(self) -> None:
        self.state_store.remove()

    def _load_state(self) -> None:
        if self.active_session is not None:
            return

        session_data = self.state_store.load()
        if not session_data:
            return

        self.active_session = TunnelSession.from_data(session_data)

    def _kill_existing(self) -> None:
        if self.active_session:
            if self.active_session.process:
                try:
                    self.active_session.process.terminate()
                except Exception:
                    pass
            elif self.active_session.pid:
                try:
                    os.kill(self.active_session.pid, signal.SIGTERM)
                except OSError:
                    pass
            self.active_session = None

        subprocess.run(["pkill", "-f", "session-manager-plugin"], check=False)
        subprocess.run(["pkill", "-f", "aws ssm start-session"], check=False)
        self._remove_state()

    def _free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("0.0.0.0", 0))
            return sock.getsockname()[1]

    def start(
        self,
        instance_id: str,
        local_port: int,
        remote_port: int,
        local_address: str = "127.0.0.1",
    ) -> TunnelSession:
        self._kill_existing()

        if local_port <= 0:
            local_port = self._free_port()

        parameters = {
            "portNumber": [str(remote_port)],
            "localPortNumber": [str(local_port)],
        }
        if local_address and local_address != "127.0.0.1":
            parameters["localAddress"] = [local_address]

        command = [
            "aws",
            "ssm",
            "start-session",
            "--target",
            instance_id,
            "--document-name",
            "AWS-StartPortForwardingSession",
            "--parameters",
            json.dumps(parameters),
        ]

        process = subprocess.Popen(command)
        try:
            pid = int(process.pid)
        except (TypeError, ValueError):
            pid = process.pid

        session = TunnelSession(
            instance_id=instance_id,
            session_id=str(process.pid),
            local_port=local_port,
            remote_port=remote_port,
            process=process,
            local_address=local_address,
            pid=pid,
            started_at=time.time(),
        )

        self.active_session = session
        self._save_state()
        return session

    def _wait_for_local_port(self, timeout: int = 10) -> None:
        if not self.active_session:
            raise RuntimeError("No active SSM tunnel session")

        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.active_session.process and self.active_session.process.poll() is not None:
                raise RuntimeError("SSM tunnel process exited before the local port opened")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                try:
                    sock.connect(("127.0.0.1", self.active_session.local_port))
                    return
                except OSError:
                    time.sleep(0.2)

        raise RuntimeError(f"Timed out waiting for local port {self.active_session.local_port} to open")

    def validate_tls(self, timeout: int = 10) -> None:
        if not self.active_session:
            raise RuntimeError("No active SSM tunnel session")

        self._wait_for_local_port(timeout=timeout)

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.active_session.process and self.active_session.process.poll() is not None:
                raise RuntimeError("SSM tunnel process exited before TLS validation completed")

            try:
                with socket.create_connection(("127.0.0.1", self.active_session.local_port), timeout=1) as sock:
                    with context.wrap_socket(sock, server_hostname="127.0.0.1"):
                        return
            except (ssl.SSLError, OSError):
                time.sleep(0.2)

        raise RuntimeError("TLS validation failed for local tunnel port")

    def ensure_alive(self, timeout: int = 3) -> bool:
        self._load_state()
        if not self.active_session:
            return False

        if self.active_session.process and self.active_session.process.poll() is not None:
            return False

        if not self.active_session.process:
            try:
                os.kill(self.active_session.pid, 0)
            except OSError:
                return False

        try:
            self.validate_tls(timeout=timeout)
            return True
        except Exception:
            return False

    def get_or_reconnect(self, instance_id: str, local_port: int = 8443, remote_port: int = 443) -> TunnelSession:
        if self.ensure_alive(timeout=3):
            return self.active_session
        return self.start(instance_id, local_port, remote_port)

    def status(self) -> dict[str, object]:
        self._load_state()
        if not self.active_session:
            return {"status": "No active session"}

        alive = self.ensure_alive(timeout=3)
        status = {
            "instance_id": self.active_session.instance_id,
            "local_port": self.active_session.local_port,
            "uptime": time.time() - self.active_session.started_at,
            "alive": alive,
        }

        if not alive:
            self._remove_state()

        return status
