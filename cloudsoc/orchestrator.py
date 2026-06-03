"""Orchestration for infrastructure, deployment, and dashboard operations.

Provides separation of concerns:
- TerraformOrchestrator: Manages Terraform lifecycle (init, validate, plan, apply, destroy)
- DeploymentOrchestrator: Manages SSM, deployment execution, and validation
- DashboardOrchestrator: Manages dashboard tunneling and access
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from rich.console import Console
from rich.panel import Panel

from cloudsoc.deployment.executor import DeploymentService
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


class DeploymentOrchestrator:
    """Manages deployment operations including SSM, playbooks, and validation.

    This orchestrator handles:
    - Waiting for SSM agent readiness
    - Running deployment playbooks
    - Validating deployment completion
    - Managing target-based deployments
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

        for target in targets:
            deployment_name = target_mapping.get(target, target)
            instance_id = instance_ids_map.get(deployment_name)

            if not instance_id:
                raise OrchestrationError(f"Missing instance ID for deployment target: {deployment_name}")

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

            if not self.deployment_service.run_deployment(
                deployment_name,
                variables=variables,
                ssm_service=self.ssm_service,
                instance_ids=[instance_id],
            ):
                error_detail = self.deployment_service.last_error or "See logs for details."
                raise OrchestrationError(
                    f"Deployment to {deployment_name} failed: {error_detail}"
                )

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

        if expose:
            self._assert_local_port_published(local_port)

        document_name = "AWS-StartPortForwardingSession"
        parameters = {
            "portNumber": [str(remote_port)],
            "localPortNumber": [str(local_port)],
        }

        command = [
            "aws",
            "ssm",
            "start-session",
            "--target",
            instance_id,
            "--document-name",
            document_name,
            "--parameters",
            json.dumps(parameters),
        ]

        local_endpoint = f"https://127.0.0.1:{local_port}"
        if expose:
            endpoint_message = (
                f"SSM is bound to localhost inside this process. "
                f"Ensure port {local_port} is exposed from your container or host environment "
                "before accessing it from outside this container.\n"
            )
            if os.getenv("CODESPACES") == "true" or os.getenv("GITHUB_CODESPACES") == "true":
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
            run_command(command)
        except ShellCommandError as e:
            raise OrchestrationError(f"Failed to start dashboard tunnel: {e}") from e

    def _assert_local_port_published(self, local_port: int) -> None:
        """Verify the requested local port is published from the dev container."""
        compose_file = Path("docker-compose.yml")
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

    def _monitor_dashboard_service(self, instance_id: str, remote_port: int) -> tuple[bool, str]:
        """Check the Wazuh dashboard HTTP service on the remote instance via SSM."""
        health_script = [
            "set +e",
            "echo '---curl-status---'",
            f"curl -k -s -o /dev/null -w '%{{http_code}}' https://127.0.0.1:{remote_port} || true",
            "echo '---opensearch-status---'",
            "curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1:9200 || true",
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

        parsed = dict(re.findall(r"^---(?P<name>[a-z-]+)---\s*\n(?P<body>.*?)(?=^---[a-z-]+---\s*$|\Z)", output, flags=re.MULTILINE | re.DOTALL))
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
