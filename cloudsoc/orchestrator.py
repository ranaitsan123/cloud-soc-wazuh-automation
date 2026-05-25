"""Deployment orchestration, inventory generation, and dashboard helpers."""

import json
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel

from cloudsoc.ansible.deploy import AnsibleService
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.aws.iam import IAMService
from cloudsoc.aws.ssm import SSMService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError
from cloudsoc.terraform.imports import ResourceImporter
from cloudsoc.utils.logger import logger
from cloudsoc.utils.shell import run_command, ShellCommandError

console = Console()
DEFAULT_INVENTORY_FILE = None


class OrchestrationError(Exception):
    """Raised when orchestration fails."""


class InventoryGenerator:
    """Builds dynamic Ansible inventory from AWS EC2 discovery."""

    def __init__(self, ec2_service: EC2Service, inventory_path: Optional[Path] = DEFAULT_INVENTORY_FILE):
        self.ec2_service = ec2_service
        self.inventory_path = inventory_path

    def generate(self, project_tag: str) -> Path:
        """Generate an inventory file for EC2 instances in the project."""
        instances = self.ec2_service.find_instances(project_tag=project_tag, states=["running"])

        if not instances:
            raise OrchestrationError("No running EC2 instances found for inventory generation")

        group_hosts: Dict[str, List[str]] = {"wazuh": [], "victims": []}

        for instance in instances:
            name = instance.tags.get("Name", "").lower()
            role = instance.tags.get("Role", "").lower()
            host_entry = (
                f"{instance.id} ansible_connection=amazon.aws.aws_ssm "
                "ansible_python_interpreter=/usr/bin/python3"
            )

            if "wazuh" in name or "wazuh" in role or "manager" in name or "manager" in role:
                group_hosts["wazuh"].append(host_entry)
            else:
                group_hosts["victims"].append(host_entry)

        if not any(group_hosts.values()):
            raise OrchestrationError("Inventory generation did not discover any hosts")

        if self.inventory_path:
            inventory_path = self.inventory_path
        else:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ini")
            inventory_path = Path(temp_file.name)
            temp_file.close()

        inventory_path.parent.mkdir(parents=True, exist_ok=True)
        lines: List[str] = []

        for group, hosts in group_hosts.items():
            if not hosts:
                continue
            lines.append(f"[{group}]")
            lines.extend(hosts)
            lines.append("")

        inventory_path.write_text("\n".join(lines).strip() + "\n")
        logger.info(f"✓ Generated inventory at {inventory_path}")
        return inventory_path


class DeploymentOrchestrator:
    """Coordinates Terraform, AWS, SSM, and Ansible deployment steps."""

    def __init__(self, settings: Optional[Settings] = None):
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
        self.ec2_service = EC2Service(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )
        self.iam_service = IAMService(profile=self.settings.project.aws.profile)
        self.ssm_service = SSMService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile
        )
        self.ansible_service = AnsibleService(playbooks_dir=Path("ansible/playbooks"))
        self.inventory_generator = InventoryGenerator(self.ec2_service)

    def apply(self, auto_approve: bool = False, var_files: Optional[List[str]] = None) -> None:
        """Apply infrastructure and perform post-apply orchestration."""
        self.tf_runner.init()
        self._import_all_existing_resources()
        self.tf_runner.validate()
        plan_file = self.tf_runner.plan(var_files=var_files or [])
        self.tf_runner.apply(plan_file=plan_file, auto_approve=auto_approve)

        self._wait_for_ssm_ready()
        inventory_path = self.inventory_generator.generate(self.settings.project.tag)
        try:
            self._validate_inventory_file(inventory_path)
            self._run_playbooks(inventory_path)
            self._validate_deployment()
            self._print_dashboard_instructions()
        finally:
            self._cleanup_inventory_file(inventory_path)

    def _import_all_existing_resources(self) -> None:
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

    def open_dashboard(self, local_port: int = 8443, remote_port: int = 443) -> None:
        """Open an SSM port-forwarding tunnel to the Wazuh dashboard."""
        instance_id = self._get_wazuh_instance_id()
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

    def _wait_for_ssm_ready(self) -> None:
        instance_ids = self._get_instance_ids()
        if not instance_ids:
            raise OrchestrationError("No EC2 instances found to wait for SSM readiness")

        for instance_id in instance_ids:
            if not self.ssm_service.wait_for_instance(instance_id, timeout=600, poll_interval=15):
                raise OrchestrationError(f"SSM agent did not become ready for instance {instance_id}")

    def _run_playbooks(self, inventory_path: Path) -> None:
        outputs = self.tf_runner.output()
        extra_vars_manager = {
            "s3_bucket_name": outputs.get("s3_bucket_name", {}).get("value", ""),
            "s3_prefix": outputs.get("s3_prefix", {}).get("value", "wazuh-docker")
        }
        extra_vars_victim = {
            "wazuh_manager_ip": outputs.get("wazuh_instance_private_ip", {}).get("value", "127.0.0.1"),
            "aws_region": self.settings.project.aws.region,
            "ecr_victim_repository_url": outputs.get("ecr_victim_repository_url", {}).get("value", "")
        }

        if not self.ansible_service.run_playbook("bootstrap.yml", inventory=str(inventory_path)):
            raise OrchestrationError("Bootstrap playbook failed")

        self._validate_remote_preconditions()

        if not self.ansible_service.run_playbook("wazuh_manager.yml", inventory=str(inventory_path), extra_vars=extra_vars_manager):
            raise OrchestrationError("Wazuh manager playbook failed")

        if not self.ansible_service.run_playbook("victim_server.yml", inventory=str(inventory_path), extra_vars=extra_vars_victim):
            raise OrchestrationError("Victim server playbook failed")

    def _validate_inventory_file(self, inventory_path: Path) -> None:
        if not inventory_path.exists():
            raise OrchestrationError(f"Inventory file not found: {inventory_path}")

        raw_lines = inventory_path.read_text().splitlines()
        groups = set()
        has_host = False
        current_group = None

        for raw_line in raw_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                current_group = line
                groups.add(line)
                continue

            if current_group in {"[wazuh]", "[victims]"}:
                has_host = True

        if not groups:
            raise OrchestrationError("Generated inventory does not contain any host groups")

        if "[localhost]" in groups:
            raise OrchestrationError("Generated inventory must not include localhost entries")

        if not has_host:
            raise OrchestrationError("Generated inventory contains no hosts in expected groups")

        logger.info(f"✓ Inventory file {inventory_path} validated: groups={sorted(groups)}")

    def _validate_remote_preconditions(self) -> None:
        instance_ids = self._get_instance_ids()
        if not instance_ids:
            raise OrchestrationError("No EC2 instances found for remote precondition validation")

        command = (
            'set -e\n'
            'python3 --version\n'
            'aws --version\n'
            'docker --version\n'
            'docker compose version\n'
        )

        for instance_id in instance_ids:
            command_id = self.ssm_service.send_command(
                instance_ids=[instance_id],
                commands=[command],
                working_directory="/tmp",
                timeout=120,
                document_name="AWS-RunShellScript"
            )

            if not command_id:
                raise OrchestrationError(f"Failed to send remote precondition check to {instance_id}")

            invocation = self.ssm_service.wait_for_command(command_id, instance_id, timeout=120, poll_interval=5)
            if not invocation:
                raise OrchestrationError(f"Remote precondition command did not complete for {instance_id}")

            if invocation.get("status") != "Success" or invocation.get("return_code") != 0:
                raise OrchestrationError(
                    f"Remote precondition validation failed for {instance_id}: "
                    f"status={invocation.get('status')} return_code={invocation.get('return_code')} "
                    f"error={invocation.get('error') or invocation.get('output')}"
                )

            logger.info(f"✓ Remote preconditions verified for {instance_id}")

    def _validate_deployment(self) -> None:
        wazuh_id = self._get_wazuh_instance_id()
        if not wazuh_id:
            raise OrchestrationError("Unable to validate deployment without Wazuh instance ID")

        if not self.ssm_service.wait_for_instance(wazuh_id, timeout=120, poll_interval=10):
            raise OrchestrationError("Deployment validation failed: Wazuh instance is not available via SSM")

        console.print(Panel("[bold green]✓ Deployment validated successfully[/bold green]", expand=False))

    def _print_dashboard_instructions(self) -> None:
        console.print(
            Panel(
                "[bold green]Deployment complete![/bold green]\n\n"
                "Next step: run [bold]cloud-soc dashboard[/bold] to open a local tunnel to the Wazuh dashboard.\n"
                "Then open [bold]https://127.0.0.1:8443[/bold] in your browser.",
                title="Cloud SOC",
                expand=False,
            )
        )

    def _get_instance_ids(self) -> List[str]:
        outputs = self.tf_runner.output()
        ids = [
            outputs.get("wazuh_instance_id", {}).get("value"),
            outputs.get("victim_instance_id", {}).get("value"),
        ]
        return [instance_id for instance_id in ids if instance_id]

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

    def _cleanup_inventory_file(self, inventory_path: Path) -> None:
        try:
            if inventory_path.exists():
                inventory_path.unlink()
                logger.debug(f"Removed temporary inventory file {inventory_path}")
        except Exception as e:
            logger.warning(f"Unable to remove temporary inventory file {inventory_path}: {e}")

    def _get_wazuh_instance_id(self) -> Optional[str]:
        outputs = self.tf_runner.output()
        return outputs.get("wazuh_instance_id", {}).get("value")
