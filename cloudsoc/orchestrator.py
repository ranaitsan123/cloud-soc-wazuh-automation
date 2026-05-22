"""Deployment orchestration, inventory generation, and dashboard helpers."""

import json
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
from cloudsoc.utils.logger import logger
from cloudsoc.utils.shell import run_command, ShellCommandError

console = Console()
DEFAULT_INVENTORY_FILE = Path("inventory/generated_hosts.ini")


class OrchestrationError(Exception):
    """Raised when orchestration fails."""


class InventoryGenerator:
    """Builds dynamic Ansible inventory from AWS EC2 discovery."""

    def __init__(self, ec2_service: EC2Service, inventory_path: Path = DEFAULT_INVENTORY_FILE):
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

        self.inventory_path.parent.mkdir(parents=True, exist_ok=True)
        lines: List[str] = []

        for group, hosts in group_hosts.items():
            if not hosts:
                continue
            lines.append(f"[{group}]")
            lines.extend(hosts)
            lines.append("")

        self.inventory_path.write_text("\n".join(lines).strip() + "\n")
        logger.info(f"✓ Generated inventory at {self.inventory_path}")
        return self.inventory_path


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
        self._ensure_iam_resources_imported()
        self.tf_runner.validate()
        plan_file = self.tf_runner.plan(var_files=var_files or [])
        self.tf_runner.apply(plan_file=plan_file, auto_approve=auto_approve)

        self._wait_for_ssm_ready()
        inventory_path = self.inventory_generator.generate(self.settings.project.tag)
        self._run_playbooks(inventory_path)
        self._validate_deployment()
        self._print_dashboard_instructions()

    def _ensure_iam_resources_imported(self) -> None:
        """Import existing IAM resources into Terraform state if they already exist."""
        known_iam_resources = [
            ("aws_iam_role.wazuh_ec2_role", "wazuh-ec2-role", "role"),
            ("aws_iam_role.victim_ec2_role", "victim-ec2-role", "role"),
            ("aws_iam_policy.wazuh_ec2_policy", "wazuh-ec2-policy", "policy"),
            ("aws_iam_policy.victim_ec2_policy", "victim-ec2-policy", "policy"),
            ("aws_iam_instance_profile.wazuh_instance_profile", "wazuh-instance-profile", "instance_profile"),
            ("aws_iam_instance_profile.victim_instance_profile", "victim-instance-profile", "instance_profile"),
        ]

        for address, name, resource_type in known_iam_resources:
            if self.tf_runner.state_contains(address):
                logger.debug(f"Terraform state already contains {address}")
                continue

            resource_id = None
            if resource_type == "role":
                role = self.iam_service.get_role(name)
                resource_id = role.name if role else None
            elif resource_type == "policy":
                resource_id = self.iam_service.get_policy_arn(name)
            elif resource_type == "instance_profile":
                profile = self.iam_service.get_instance_profile(name)
                resource_id = profile.get("InstanceProfileName") if profile else None

            if resource_id:
                logger.info(f"Found existing IAM resource {name}, importing {address} into Terraform state")
                self.tf_runner.import_resource(address, resource_id)
            else:
                logger.debug(f"No existing IAM {resource_type} found for {name}; Terraform will create it")

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

        if not self.ansible_service.run_playbook("wazuh_manager.yml", inventory=str(inventory_path), extra_vars=extra_vars_manager):
            raise OrchestrationError("Wazuh manager playbook failed")

        if not self.ansible_service.run_playbook("victim_server.yml", inventory=str(inventory_path), extra_vars=extra_vars_victim):
            raise OrchestrationError("Victim server playbook failed")

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

    def _get_wazuh_instance_id(self) -> Optional[str]:
        outputs = self.tf_runner.output()
        return outputs.get("wazuh_instance_id", {}).get("value")
