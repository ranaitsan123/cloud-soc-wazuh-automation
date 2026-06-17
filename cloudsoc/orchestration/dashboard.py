from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional

import yaml
from rich.console import Console
from rich.panel import Panel

from cloudsoc.aws.ssm import SSMService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.models.outputs import InfrastructureOutputs
from cloudsoc.orchestration.errors import OrchestrationError
from cloudsoc.orchestration.tunnel import SSMDashboardTunnelManager
from cloudsoc.utils.logger import logger

console = Console()


class DashboardOrchestrator:
    """Manages Wazuh dashboard access via SSM port forwarding."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.ssm_service = SSMService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile,
        )
        self.tunnel_manager = SSMDashboardTunnelManager()

    def open_tunnel(
        self,
        outputs: InfrastructureOutputs,
        local_port: int = 8443,
        remote_port: int = 443,
        expose: bool = False,
    ) -> None:
        instance_id = outputs.wazuh_instance_id
        if not instance_id:
            raise OrchestrationError("Wazuh instance ID could not be determined for dashboard access")

        if not self.ssm_service.wait_for_instance(instance_id, timeout=120, poll_interval=10):
            raise OrchestrationError("SSM agent is not online for the Wazuh instance")

        dashboard_ready, diagnostics = self._monitor_dashboard_service(instance_id, remote_port)
        if dashboard_ready:
            status_message = "Wazuh dashboard service is responsive on the instance."
        else:
            status_message = (
                "Warning: Wazuh dashboard service did not respond on the remote instance. "
                "The tunnel will still be opened if possible."
            )
            if diagnostics:
                status_message += f"\n\nRemote diagnostics:\n{diagnostics}"

        if expose and not self._is_codespaces():
            self._assert_local_port_published(local_port)

        local_endpoint = f"https://127.0.0.1:{local_port}"
        if expose:
            endpoint_message = (
                f"SSM tunnel is now accessible via {local_endpoint} if port {local_port} "
                "is exposed from the container or forwarded by your environment.\n"
            )
            if self._is_codespaces():
                endpoint_message += (
                    f"In Codespaces, forward port {local_port} in the Ports tab and then open {local_endpoint}.\n"
                )
        else:
            endpoint_message = f"Open [bold]{local_endpoint}[/bold] in your browser.\n"

        console.print(
            Panel(
                f"[bold green]Dashboard tunneling started[/bold green]\n\n"
                f"{status_message}\n\n"
                f"{endpoint_message}"
                "Use Ctrl+C to stop the session.",
                title="Wazuh Dashboard",
                expand=False,
            )
        )

        try:
            tunnel_address = "0.0.0.0" if expose else "127.0.0.1"
            session = self.tunnel_manager.start(
                instance_id,
                local_port,
                remote_port,
                local_address=tunnel_address,
            )
            self.tunnel_manager.validate_tls(timeout=10)
            session.process.wait()
        except KeyboardInterrupt:
            self.tunnel_manager._kill_existing()
            raise
        except (FileNotFoundError, RuntimeError, OSError) as e:
            self.tunnel_manager._kill_existing()
            raise OrchestrationError(f"Failed to start dashboard tunnel: {e}") from e

    def status(self) -> Dict[str, object]:
        return self.tunnel_manager.status()

    def _assert_local_port_published(self, local_port: int) -> None:
        compose_file = Path("docker-compose.yml")
        if self._is_codespaces():
            return

        if not compose_file.exists():
            raise OrchestrationError(
                "Unable to validate --expose because docker-compose.yml was not found in the current directory. "
                "Run from the repository root or expose the port manually."
            )

        try:
            compose_config = yaml.safe_load(compose_file.read_text()) or {}
        except Exception as e:
            raise OrchestrationError(
                f"Failed to parse docker-compose.yml for --expose validation: {e}"
            ) from e

        services = compose_config.get("services", {})
        for service in services.values():
            ports = service.get("ports", []) or []
            for port_mapping in ports:
                if isinstance(port_mapping, str):
                    parts = port_mapping.split(":")
                    if len(parts) == 2:
                        host_port, container_port = parts
                    elif len(parts) == 3:
                        _, host_port, container_port = parts
                    else:
                        continue

                    if host_port == str(local_port) and container_port == str(local_port):
                        return
                elif isinstance(port_mapping, dict):
                    if str(port_mapping.get("published", "")) == str(local_port) and str(port_mapping.get("target", "")) == str(local_port):
                        return

        raise OrchestrationError(
            f"Port {local_port} is not published from the dev container. "
            f"Add a port mapping such as `ports:\n  - \"{local_port}:{local_port}\"` to your docker-compose.yml."
        )

    def _is_codespaces(self) -> bool:
        return os.getenv("CODESPACES") == "true" or os.getenv("GITHUB_CODESPACES") == "true"

    def _monitor_dashboard_service(self, instance_id: str, remote_port: int) -> tuple[bool, str]:
        health_script = [
            "set +e",
            "echo '---curl-status---'",
            f"curl -k -s -o /dev/null -w '%{{http_code}}\n' https://127.0.0.1:{remote_port} || true",
            "echo '---opensearch-status---'",
            "curl -k -s -o /dev/null -w '%{http_code}\n' https://127.0.0.1:9200 || true",
            "echo '---docker-ps---'",
            "docker compose -f /opt/wazuh/docker-compose.yml ps || true",
            "echo '---dashboard-logs---'",
            "docker compose -f /opt/wazuh/docker-compose.yml logs --tail 40 wazuh.dashboard || true",
            "echo '---indexer-logs---'",
            "docker compose -f /opt/wazuh/docker-compose.yml logs --tail 40 wazuh.indexer || true",
        ]

        command_id = self.ssm_service.send_command(
            instance_ids=[instance_id],
            commands=["\n".join(health_script)],
            working_directory="/tmp",
            timeout=120,
            document_name="AWS-RunShellScript",
        )

        if not command_id:
            logger.warning("Unable to send dashboard health check command via SSM")
            return False, "Unable to send SSM dashboard health check command."

        invocation = self.ssm_service.wait_for_command(command_id, instance_id, timeout=120, poll_interval=5)
        if not invocation:
            logger.warning("Dashboard health check command did not complete")
            return False, "Dashboard health check command did not complete."

        status = invocation.get("status")
        return_code = invocation.get("return_code")
        output = invocation.get("output", "")
        error = invocation.get("error", "").strip()

        if status != "Success" or return_code != 0:
            diagnostics = []
            if output:
                diagnostics.append(output.strip())
            if error:
                diagnostics.append(error)
            return False, "\n".join(diagnostics).strip()

        parsed = dict(re.findall(r"---(?P<name>[a-z-]+)---(.*?)(?=---[a-z-]+---|\Z)", output, flags=re.DOTALL))
        curl_status = parsed.get("curl-status", "").strip().splitlines()[0] if parsed.get("curl-status") else ""
        opensearch_status = parsed.get("opensearch-status", "").strip().splitlines()[0] if parsed.get("opensearch-status") else ""

        dashboard_ready = curl_status in {"200", "302", "301"}
        diagnostics_parts = []

        if not dashboard_ready:
            diagnostics_parts.append(f"Dashboard returned HTTP status {curl_status or 'unknown'}.")

        if opensearch_status and opensearch_status != "200":
            diagnostics_parts.append(f"OpenSearch returned HTTP status {opensearch_status}.")

        docker_ps = parsed.get("docker-ps", "").strip()
        dashboard_logs = parsed.get("dashboard-logs", "").strip()
        indexer_logs = parsed.get("indexer-logs", "").strip()

        if docker_ps:
            diagnostics_parts.append(f"docker compose ps:\n{docker_ps}")
        if dashboard_logs:
            diagnostics_parts.append(f"dashboard logs:\n{dashboard_logs}")
        if indexer_logs:
            diagnostics_parts.append(f"indexer logs:\n{indexer_logs}")

        diagnostics = "\n\n".join(diagnostics_parts).strip()

        if dashboard_ready:
            if diagnostics:
                diagnostics = f"Dashboard is responding, but diagnostics show potential issues:\n{diagnostics}"
            return True, diagnostics

        return False, diagnostics or "Dashboard health check failed and no diagnostics were captured."
