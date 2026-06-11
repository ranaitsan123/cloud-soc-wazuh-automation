"""Orchestration for infrastructure, deployment, and dashboard operations.

Provides separation of concerns:
- TerraformOrchestrator: Manages Terraform lifecycle (init, validate, plan, apply, destroy)
- DeploymentOrchestrator: Manages SSM, deployment execution, and validation
- DashboardOrchestrator: Manages dashboard tunneling and access
"""

import json
import os
import re
import socket
import ssl
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
import signal
from typing import Dict, List, Optional, Tuple

import yaml
from rich.console import Console
from rich.panel import Panel

from cloudsoc.deployment.executor import DeploymentService
from cloudsoc.aws.ecr import ECRService
from cloudsoc.aws.iam import IAMService
from cloudsoc.aws.ssm import SSMService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError
from cloudsoc.terraform.imports import ResourceImporter
from cloudsoc.utils.logger import logger
from cloudsoc.utils.shell import run_command, ShellCommandError

console = Console()


class OrchestrationError(Exception):
    """Raised when orchestration fails."""


@dataclass
class TunnelSession:
    instance_id: str
    session_id: str
    local_port: int
    remote_port: int
    process: Optional[subprocess.Popen]
    started_at: float
    pid: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "session_id": self.session_id,
            "local_port": self.local_port,
            "remote_port": self.remote_port,
            "pid": self.pid,
            "started_at": self.started_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TunnelSession":
        return cls(
            instance_id=data["instance_id"],
            session_id=data["session_id"],
            local_port=data["local_port"],
            remote_port=data["remote_port"],
            process=None,
            pid=data["pid"],
            started_at=data["started_at"],
        )


class SSMDashboardTunnelManager:
    def __init__(self) -> None:
        self.active_session: Optional[TunnelSession] = None

    @property
    def _state_file(self) -> Path:
        state_dir = Path.home() / ".cloud-soc"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "dashboard_tunnel.json"

    def _save_state(self) -> None:
        if not self.active_session:
            return

        self._state_file.write_text(json.dumps(self.active_session.to_dict()))

    def _remove_state(self) -> None:
        try:
            self._state_file.unlink()
        except FileNotFoundError:
            pass

    def _load_state(self) -> None:
        if self.active_session is not None:
            return

        if not self._state_file.exists():
            return

        try:
            data = json.loads(self._state_file.read_text())
            self.active_session = TunnelSession.from_dict(data)
        except Exception:
            self._remove_state()

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
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def start(self, instance_id: str, local_port: int, remote_port: int) -> TunnelSession:
        self._kill_existing()

        if local_port <= 0:
            local_port = self._free_port()

        command = [
            "aws",
            "ssm",
            "start-session",
            "--target",
            instance_id,
            "--document-name",
            "AWS-StartPortForwardingSession",
            "--parameters",
            json.dumps({
                "portNumber": [str(remote_port)],
                "localPortNumber": [str(local_port)],
            }),
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
            if self.active_session.process.poll() is not None:
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


class TerraformOrchestrator:
    """Manages Terraform infrastructure lifecycle operations."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize Terraform orchestrator with configuration.

        Args:
            settings: Optional Settings object. Uses get_settings() if not provided.
        """
        self.settings = settings or get_settings()
        backend_config = {
            "bucket": self.settings.project.terraform.backend_bucket,
            "key": self.settings.project.terraform.backend_key,
            "region": self.settings.project.terraform.backend_region,
        }
        if self.settings.project.terraform.backend_dynamodb_table:
            backend_config["dynamodb_table"] = self.settings.project.terraform.backend_dynamodb_table

        self.tf_runner = TerraformRunner(
            terraform_dir=self.settings.project.terraform.dir,
            auto_approve=self.settings.project.terraform.auto_approve,
            backend_config=backend_config,
        )

    def init(self) -> None:
        """Initialize Terraform configuration."""
        self.tf_runner.init()

    def import_all_existing_resources(self) -> None:
        """Import all existing AWS resources into Terraform state to prevent recreation."""
        try:
            importer = ResourceImporter(
                tf_runner=self.tf_runner,
                settings=self.settings
            )
            importer.import_all_existing_resources()
            logger.info("✓ Resource import check completed")
        except Exception as e:
            logger.warning(f"Resource import encountered an issue (non-critical): {e}")
            logger.info("Proceeding with deployment - Terraform will handle creation of missing resources")

    def validate(self) -> None:
        """Validate Terraform configuration."""
        self.tf_runner.validate()

    def plan(self, var_files: Optional[List[str]] = None) -> str:
        """Plan infrastructure changes.

        Args:
            var_files: Optional list of Terraform variable file paths.

        Returns:
            Path to the generated plan file.
        """
        return self.tf_runner.plan(var_files=var_files or [])

    def apply(self, plan_file: str, auto_approve: bool = False) -> None:
        """Apply infrastructure changes.

        Args:
            plan_file: Path to the Terraform plan file.
            auto_approve: Whether to skip approval prompt.
        """
        self.tf_runner.apply(plan_file=plan_file, auto_approve=auto_approve)

    def destroy(self, auto_approve: bool = False) -> None:
        """Destroy infrastructure.

        Args:
            auto_approve: Whether to skip approval prompt.
        """
        self.tf_runner.destroy(auto_approve=auto_approve)

    def output(self) -> Dict:
        """Get Terraform outputs.

        Returns:
            Dictionary of Terraform outputs.
        """
        return self.tf_runner.output()


class BuildOrchestrator:
    """Manages image build workflows triggered via GitHub Actions."""

    WORKFLOW_TARGETS = {
        "victim": {
            "workflow_file": "build-victim-image.yml",
            "ecr_repository": "cloud-soc-victim",
        },
    }

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.ecr_service = ECRService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile,
        )

    def _resolve_build_targets(self, targets: Optional[List[str]] = None) -> List[str]:
        if not targets or any(target.lower() == "all" for target in targets):
            return list(self.WORKFLOW_TARGETS.keys())

        resolved = []
        for target in targets:
            normalized_target = target.lower()
            if normalized_target not in self.WORKFLOW_TARGETS:
                raise OrchestrationError(
                    f"Unsupported build target: {target}. "
                    f"Supported targets: {', '.join(self.WORKFLOW_TARGETS)}"
                )
            resolved.append(normalized_target)

        return resolved

    def build_targets(
        self,
        targets: Optional[List[str]] = None,
        wait: bool = False,
        ref: Optional[str] = None,
    ) -> None:
        build_targets = self._resolve_build_targets(targets)

        for build_target in build_targets:
            self._build_target(build_target, wait=wait, ref=ref)

    def ensure_image_exists(self, target: str) -> None:
        target_key = target.lower()
        if target_key not in self.WORKFLOW_TARGETS:
            raise OrchestrationError(f"Unsupported build target: {target}")

        repo_name = self.WORKFLOW_TARGETS[target_key]["ecr_repository"]
        repo = self.ecr_service.get_repository(repo_name)

        if not repo:
            raise OrchestrationError(
                f"No ECR repository found for {repo_name}."
                f" Run:\n\n  cloud-soc build {target_key} --wait\n\n"
                "or\n\n  cloud-soc up --build\n"
            )

        images = self.ecr_service.list_images(repository_name=repo_name)
        if not images:
            raise OrchestrationError(
                f"No image found in ECR repository {repo_name}."
                f" Run:\n\n  cloud-soc build {target_key} --wait\n\n"
                "or\n\n  cloud-soc up --build\n"
            )

    def _build_target(self, target: str, wait: bool = False, ref: Optional[str] = None) -> None:
        workflow_file = self.WORKFLOW_TARGETS[target]["workflow_file"]

        console.print(
            Panel(
                f"[bold cyan]Cloud SOC[/bold cyan] - [yellow]Build {target} Image[/yellow]",
                expand=False,
            )
        )

        command = ["gh", "workflow", "run", workflow_file]
        if ref:
            command.extend(["--ref", ref])

        try:
            result = run_command(command, capture_output=True)
            output = (result.stdout or "") + (result.stderr or "")
            workflow_run_id = self._parse_workflow_run_id(output)

            console.print(
                Panel(
                    f"Triggered GitHub workflow [bold]{workflow_file}[/bold] for target [bold]{target}[/bold].\n"
                    f"Workflow run id: [bold]{workflow_run_id}[/bold]",
                    expand=False,
                )
            )

            if wait:
                console.print("Waiting for workflow completion...")
                run_command(["gh", "run", "watch", workflow_run_id, "--exit-status"])
                console.print(
                    Panel(
                        f"[bold green]✓ Build workflow complete for {target}[/bold green]",
                        expand=False,
                    )
                )

        except ShellCommandError as e:
            raise OrchestrationError(
                f"Failed to trigger build workflow for {target}: {e}"
            ) from e

    def _parse_workflow_run_id(self, output: str) -> str:
        match = re.search(r"Created workflow run (\d+)", output)
        if not match:
            match = re.search(r"/actions/runs/(\d+)", output)
        if not match:
            raise OrchestrationError(
                "Unable to determine workflow run id from GitHub CLI output. "
                "Ensure you are in the repository root and the workflow file exists."
            )

        return match.group(1)


class DeploymentOrchestrator:
    """Manages deployment operations including SSM, playbooks, and validation.

    This orchestrator handles:
    - Waiting for SSM agent readiness
    - Running deployment playbooks
    - Validating deployment completion
    - Managing target-based deployments
    - Persisting deployment state and status
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize deployment orchestrator.

        Args:
            settings: Optional Settings object. Uses get_settings() if not provided.
        """
        self.settings = settings or get_settings()
        self.ssm_service = SSMService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )
        self.deployment_service = DeploymentService(deployment_dir=Path("playbooks"))

    @property
    def deployment_state_file(self) -> Path:
        state_dir = Path.home() / ".cloud-soc"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir / "deployment_state.json"

    def _load_deployment_state(self) -> dict:
        if not self.deployment_state_file.exists():
            return {}

        try:
            return json.loads(self.deployment_state_file.read_text())
        except Exception:
            return {}

    def _save_deployment_state(self, state: dict) -> None:
        self.deployment_state_file.write_text(json.dumps(state, indent=2))

    def _initialize_deployment_state(self, deployment_names: List[str]) -> dict:
        now = time.time()
        state = {
            "last_deployment": {
                "started_at": now,
                "finished_at": None,
                "status": "in_progress",
                "targets": {
                    name: {
                        "status": "pending",
                        "started_at": None,
                        "finished_at": None,
                        "error": "",
                    }
                    for name in deployment_names
                },
            }
        }
        self._save_deployment_state(state)
        return state

    def _update_target_state(self, state: dict, deployment_name: str, status: str, error: str = "") -> None:
        target_state = state["last_deployment"]["targets"].get(deployment_name)
        if not target_state:
            return

        now = time.time()
        if status == "in_progress":
            target_state["started_at"] = now
        target_state["finished_at"] = now if status in {"success", "failed"} else None
        target_state["status"] = status
        target_state["error"] = error
        self._save_deployment_state(state)

    def get_deployment_status(self) -> dict[str, object]:
        state = self._load_deployment_state()
        last = state.get("last_deployment")
        if not last:
            return {"status": "No deployment history recorded"}

        success = all(
            target.get("status") == "success"
            for target in last.get("targets", {}).values()
        )
        if last.get("status") == "in_progress" and success:
            last["status"] = "success"
            self._save_deployment_state(state)

        return last

    def wait_for_ssm_ready(self, instance_ids: List[str], timeout: int = 600, poll_interval: int = 15) -> None:
        """Wait for SSM agent to be ready on instances.

        Args:
            instance_ids: List of EC2 instance IDs to wait for.
            timeout: Maximum time to wait in seconds.
            poll_interval: Interval between status checks in seconds.

        Raises:
            OrchestrationError: If SSM agent does not become ready.
        """
        if not instance_ids:
            raise OrchestrationError("No EC2 instances provided for SSM readiness check")

        for instance_id in instance_ids:
            if not self.ssm_service.wait_for_instance(instance_id, timeout=timeout, poll_interval=poll_interval):
                raise OrchestrationError(f"SSM agent did not become ready for instance {instance_id}")

    def deploy_targets(
        self,
        terraform_outputs: Dict,
        targets: Optional[List[str]] = None,
        skip_validation: bool = False
    ) -> None:
        """Deploy to specified targets using Terraform outputs.

        Args:
            terraform_outputs: Dictionary of Terraform outputs.
            targets: List of deployment targets. If None or empty, deploys to all configured targets.
                    Supported: 'wazuh', 'victim', or any deployment in playbooks/ directory.
            skip_validation: Whether to skip deployment validation.

        Raises:
            OrchestrationError: If deployment fails.
        """
        # Default to all configured targets if none specified
        if not targets:
            targets = ["wazuh_manager", "victim_server"]

        # Map user-friendly names to deployment names
        target_mapping = {
            "wazuh": "wazuh_manager",
            "victim": "victim_server",
            "wazuh_manager": "wazuh_manager",
            "victim_server": "victim_server",
        }

        # Get instance IDs from outputs
        instance_ids_map = {
            "wazuh_manager": terraform_outputs.get("wazuh_instance_id", {}).get("value"),
            "victim_server": terraform_outputs.get("victim_instance_id", {}).get("value"),
        }

        build_orchestrator = BuildOrchestrator(settings=self.settings)

        # Validate image existence for targets that depend on built images
        for target in targets:
            deployment_name = target_mapping.get(target, target)
            if deployment_name == "victim_server":
                build_orchestrator.ensure_image_exists("victim")

        deployment_names = [target_mapping.get(target, target) for target in targets]
        state = self._initialize_deployment_state(deployment_names)

        try:
            for target in targets:
                deployment_name = target_mapping.get(target, target)
                instance_id = instance_ids_map.get(deployment_name)

                if not instance_id:
                    raise OrchestrationError(f"Missing instance ID for deployment target: {deployment_name}")

                self._update_target_state(state, deployment_name, "in_progress")

                # Prepare deployment-specific variables
                if deployment_name == "wazuh_manager":
                    variables = {
                        "s3_bucket_name": terraform_outputs.get("s3_bucket_name", {}).get("value", ""),
                        "s3_prefix": terraform_outputs.get("s3_prefix", {}).get("value", "wazuh-docker"),
                    }
                elif deployment_name == "victim_server":
                    variables = {
                        "wazuh_manager_ip": terraform_outputs.get("wazuh_instance_private_ip", {}).get("value", "127.0.0.1"),
                        "aws_region": self.settings.project.aws.region,
                        "ecr_victim_repository_url": terraform_outputs.get("ecr_victim_repository_url", {}).get("value", ""),
                    }
                else:
                    # For future deployments, pass all outputs as variables
                    variables = terraform_outputs

                success = self.deployment_service.run_deployment(
                    deployment_name,
                    variables=variables,
                    ssm_service=self.ssm_service,
                    instance_ids=[instance_id],
                )

                if success:
                    self._update_target_state(state, deployment_name, "success")
                    continue

                error_detail = self.deployment_service.last_error or "See logs for details."
                self._update_target_state(state, deployment_name, "failed", error=error_detail)
                raise OrchestrationError(
                    f"Deployment to {deployment_name} failed: {error_detail}"
                )
        except OrchestrationError:
            state["last_deployment"]["finished_at"] = time.time()
            state["last_deployment"]["status"] = "failed"
            self._save_deployment_state(state)
            raise

        state["last_deployment"]["finished_at"] = time.time()
        state["last_deployment"]["status"] = "success"
        self._save_deployment_state(state)

    def validate_deployment(self, terraform_outputs: Dict) -> None:
        """Validate that deployment is healthy.

        Args:
            terraform_outputs: Dictionary of Terraform outputs.

        Raises:
            OrchestrationError: If validation fails.
        """
        wazuh_id = terraform_outputs.get("wazuh_instance_id", {}).get("value")
        if not wazuh_id:
            raise OrchestrationError("Unable to validate deployment without Wazuh instance ID")

        if not self.ssm_service.wait_for_instance(wazuh_id, timeout=120, poll_interval=10):
            raise OrchestrationError("Deployment validation failed: Wazuh instance is not available via SSM")

        dashboard = DashboardOrchestrator(settings=self.settings)
        dashboard_ready, diagnostics = dashboard._monitor_dashboard_service(wazuh_id, remote_port=443)
        if not dashboard_ready:
            message = "Deployment validation failed: remote dashboard health check failed."
            if diagnostics:
                message += f"\n{diagnostics}"
            raise OrchestrationError(message)

        console.print(Panel("[bold green]✓ Deployment validated successfully[/bold green]", expand=False))


class DashboardOrchestrator:
    """Manages Wazuh dashboard access via SSM port forwarding."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize dashboard orchestrator.

        Args:
            settings: Optional Settings object. Uses get_settings() if not provided.
        """
        self.settings = settings or get_settings()
        self.ssm_service = SSMService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )
        self.tunnel_manager = SSMDashboardTunnelManager()

    def open_tunnel(
        self,
        terraform_outputs: Dict,
        local_port: int = 8443,
        remote_port: int = 443,
        expose: bool = False,
    ) -> None:
        """Open an SSM port-forwarding tunnel to the Wazuh dashboard.

        Args:
            terraform_outputs: Dictionary of Terraform outputs.
            local_port: Local port for port forwarding.
            remote_port: Remote dashboard port on the Wazuh instance.
            expose: Whether to indicate the port should be exposed by the container/host environment.

        Raises:
            OrchestrationError: If tunnel cannot be opened.
        """
        instance_id = terraform_outputs.get("wazuh_instance_id", {}).get("value")
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
            session = self.tunnel_manager.start(instance_id, local_port, remote_port)
            self.tunnel_manager.validate_tls(timeout=10)
            session.process.wait()
        except KeyboardInterrupt:
            self.tunnel_manager._kill_existing()
            raise
        except (FileNotFoundError, RuntimeError, OSError) as e:
            self.tunnel_manager._kill_existing()
            raise OrchestrationError(f"Failed to start dashboard tunnel: {e}") from e

    def status(self) -> dict[str, object]:
        """Get current dashboard tunnel status."""
        return self.tunnel_manager.status()

    def _assert_local_port_published(self, local_port: int) -> None:
        """Verify the requested local port is published from the dev container."""
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
        """Check the Wazuh dashboard HTTP service on the remote instance via SSM."""
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
            document_name="AWS-RunShellScript"
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
