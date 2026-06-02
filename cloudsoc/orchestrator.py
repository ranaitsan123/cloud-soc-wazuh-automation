"""Orchestration for infrastructure, deployment, and dashboard operations.

Provides separation of concerns:
- TerraformOrchestrator: Manages Terraform lifecycle (init, validate, plan, apply, destroy)
- DeploymentOrchestrator: Manages SSM, deployment execution, and validation
- DashboardOrchestrator: Manages dashboard tunneling and access
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

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
        self.deployment_service = DeploymentService(deployment_dir=Path("deployment"))

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
                    Supported: 'wazuh', 'victim', or any deployment in deployment/ directory.
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
                raise OrchestrationError(f"Deployment to {deployment_name} failed")

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

    def open_tunnel(self, terraform_outputs: Dict, local_port: int = 8443, remote_port: int = 443) -> None:
        """Open an SSM port-forwarding tunnel to the Wazuh dashboard.

        Args:
            terraform_outputs: Dictionary of Terraform outputs.
            local_port: Local port for port forwarding.
            remote_port: Remote dashboard port on the Wazuh instance.

        Raises:
            OrchestrationError: If tunnel cannot be opened.
        """
        instance_id = terraform_outputs.get("wazuh_instance_id", {}).get("value")
        if not instance_id:
            raise OrchestrationError("Wazuh instance ID could not be determined for dashboard access")

        if not self.ssm_service.wait_for_instance(instance_id, timeout=120, poll_interval=10):
            raise OrchestrationError("SSM agent is not online for the Wazuh instance")

        dashboard_ready = self._monitor_dashboard_service(instance_id, remote_port)
        if dashboard_ready:
            status_message = "Wazuh dashboard service is responsive on the instance."
        else:
            status_message = "Warning: Wazuh dashboard service did not respond on the remote instance. The tunnel will still be opened if possible."

        command = [
            "aws",
            "ssm",
            "start-session",
            "--target",
            instance_id,
            "--document-name",
            "AWS-StartPortForwardingSessionToRemoteHost",
            "--parameters",
            json.dumps({
                "host": ["127.0.0.1"],
                "portNumber": [str(remote_port)],
                "localPortNumber": [str(local_port)]
            }),
        ]

        console.print(
            Panel(
                f"[bold green]Dashboard tunneling started[/bold green]\n\n"
                f"{status_message}\n\n"
                f"Open [bold]https://127.0.0.1:{local_port}[/bold] in your browser.\n"
                "Use Ctrl+C to stop the session.",
                title="Wazuh Dashboard",
                expand=False,
            )
        )

        try:
            run_command(command)
        except ShellCommandError as e:
            raise OrchestrationError(f"Failed to start dashboard tunnel: {e}") from e

    def _monitor_dashboard_service(self, instance_id: str, remote_port: int) -> bool:
        """Check the Wazuh dashboard HTTP service on the remote instance via SSM."""
        command = [
            f"curl -k -s -o /dev/null -w '%{{http_code}}' https://127.0.0.1:{remote_port}"
        ]
        command_id = self.ssm_service.send_command(
            instance_ids=[instance_id],
            commands=command,
            working_directory="/tmp",
            timeout=60,
            document_name="AWS-RunShellScript"
        )

        if not command_id:
            logger.warning("Unable to send dashboard health check command via SSM")
            return False

        invocation = self.ssm_service.wait_for_command(command_id, instance_id, timeout=90, poll_interval=5)
        if not invocation:
            logger.warning("Dashboard health check command did not complete")
            return False

        if invocation.get("status") != "Success" or invocation.get("return_code") != 0:
            logger.warning(
                f"Dashboard health check failed: status={invocation.get('status')} return_code={invocation.get('return_code')}"
            )
            return False

        return invocation.get("output", "") == "200"
