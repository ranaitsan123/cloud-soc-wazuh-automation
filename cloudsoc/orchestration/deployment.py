from __future__ import annotations

import functools
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel

from cloudsoc.aws.ssm import SSMService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.deployment.executor import DeploymentService
from cloudsoc.models.deployment import DeploymentState, DeploymentTargetState
from cloudsoc.models.outputs import InfrastructureOutputs
from cloudsoc.orchestration.build import BuildOrchestrator
from cloudsoc.orchestration.dashboard import DashboardOrchestrator
from cloudsoc.orchestration.errors import OrchestrationError
from cloudsoc.services.deployment_state import DeploymentStateStore

console = Console()


class DeploymentOrchestrator:
    """Manages deployment operations including SSM, playbooks, and validation."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.ssm_service = SSMService(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile,
        )
        self.deployment_service = DeploymentService(deployment_dir=Path("playbooks"))
        self.state_store = DeploymentStateStore()

    def wait_for_ssm_ready(self, instance_ids: List[str], timeout: int = 600, poll_interval: int = 15) -> None:
        if not instance_ids:
            raise OrchestrationError("No EC2 instances provided for SSM readiness check")

        for instance_id in instance_ids:
            if not self.ssm_service.wait_for_instance(instance_id, timeout=timeout, poll_interval=poll_interval):
                raise OrchestrationError(f"SSM agent did not become ready for instance {instance_id}")

    def deployment_logs_dir(self) -> Path:
        state_dir = Path.home() / ".cloud-soc"
        state_dir.mkdir(parents=True, exist_ok=True)
        logs_dir = state_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    def _save_deployment_log(self, deployment_name: str, instance_id: str, error_detail: str) -> Path:
        timestamp = time.strftime("%Y-%m-%dT%H-%M-%S", time.gmtime())
        log_filename = self.deployment_logs_dir() / f"deployment-{deployment_name}-{instance_id}-{timestamp}.log"
        log_contents = (
            f"Deployment: {deployment_name}\n"
            f"Instance: {instance_id}\n"
            f"Timestamp: {timestamp}Z\n\n"
            f"Error:\n{error_detail}\n"
        )
        log_filename.write_text(log_contents)
        return log_filename

    @property
    def deployment_state_file(self) -> Path:
        return self.state_store.path

    def list_deployment_logs(self, limit: Optional[int] = None) -> List[Path]:
        logs_dir = self.deployment_logs_dir()
        if not logs_dir.exists():
            return []

        log_files = sorted(
            logs_dir.glob("deployment-*.log"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        return log_files[:limit] if limit else log_files

    def get_deployment_status(self) -> Dict[str, object]:
        state = self.state_store.load()
        if not state:
            return {"status": "No deployment history recorded"}

        success = all(
            target.status == "success"
            for target in state.targets.values()
        )
        if state.status == "in_progress" and success:
            state.status = "success"
            self.state_store.save(state)

        return {
            "status": state.status,
            "started_at": state.started_at,
            "finished_at": state.finished_at,
            "targets": {
                name: {
                    "status": target.status,
                    "started_at": target.started_at,
                    "finished_at": target.finished_at,
                    "current_task": target.current_task,
                    "error": target.error,
                    "error_detail": target.error_detail,
                }
                for name, target in state.targets.items()
            },
        }

    def deploy_targets(
        self,
        outputs: InfrastructureOutputs,
        targets: Optional[List[str]] = None,
        skip_validation: bool = False,
    ) -> None:
        if not targets:
            targets = ["wazuh_manager", "victim_server"]

        target_mapping = {
            "wazuh": "wazuh_manager",
            "victim": "victim_server",
            "wazuh_manager": "wazuh_manager",
            "victim_server": "victim_server",
        }

        instance_ids_map = {
            "wazuh_manager": outputs.wazuh_instance_id,
            "victim_server": outputs.victim_instance_id,
        }

        build_orchestrator = BuildOrchestrator(settings=self.settings)
        for target in targets:
            deployment_name = target_mapping.get(target, target)
            if deployment_name == "victim_server":
                build_orchestrator.ensure_image_exists("victim")

        deployment_names = [target_mapping.get(target, target) for target in targets]
        state = self.state_store.initialize(deployment_names)

        try:
            for target in targets:
                deployment_name = target_mapping.get(target, target)
                instance_id = instance_ids_map.get(deployment_name)

                if not instance_id:
                    raise OrchestrationError(f"Missing instance ID for deployment target: {deployment_name}")

                self._update_target_state(state, deployment_name, "in_progress")

                if deployment_name == "wazuh_manager":
                    variables = {
                        "s3_bucket_name": outputs.s3_bucket_name or "",
                        "s3_prefix": outputs.s3_prefix or "wazuh-docker",
                    }
                elif deployment_name == "victim_server":
                    variables = {
                        "s3_bucket_name": outputs.s3_bucket_name or "",
                        "wazuh_manager_ip": outputs.wazuh_instance_private_ip or "127.0.0.1",
                        "aws_region": self.settings.project.aws.region,
                        "ecr_victim_repository_url": outputs.ecr_victim_repository_url or "",
                    }
                else:
                    variables = outputs.raw

                success = self.deployment_service.run_deployment(
                    deployment_name,
                    variables=variables,
                    ssm_service=self.ssm_service,
                    instance_ids=[instance_id],
                    progress_callback=functools.partial(
                        self._update_target_progress,
                        state,
                        deployment_name,
                    ),
                )

                if success:
                    self._update_target_state(state, deployment_name, "success")
                    continue

                error_detail = self.deployment_service.last_error_detail or self.deployment_service.last_error or "See logs for details."
                self._update_target_state(
                    state,
                    deployment_name,
                    "failed",
                    error=self.deployment_service.last_error or "Deployment failed",
                    error_detail=error_detail,
                )
                log_file = self._save_deployment_log(deployment_name, instance_id, error_detail)
                raise OrchestrationError(
                    f"Deployment to {deployment_name} failed: {self.deployment_service.last_error or 'Deployment failed'}\n"
                    f"Detailed log saved to {log_file}"
                )
        except OrchestrationError:
            state.status = "failed"
            state.finished_at = time.time()
            self.state_store.save(state)
            raise

        state.status = "success"
        state.finished_at = time.time()
        self.state_store.save(state)

    def validate_deployment(self, outputs: InfrastructureOutputs) -> None:
        wazuh_id = outputs.wazuh_instance_id
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

    def _update_target_state(
        self,
        state: DeploymentState,
        deployment_name: str,
        status: str,
        error: str = "",
        error_detail: str = "",
    ) -> None:
        target_state = state.targets.get(deployment_name)
        if not target_state:
            return

        now = time.time()
        if status == "in_progress":
            target_state.started_at = now
        target_state.finished_at = now if status in {"success", "failed"} else None
        target_state.status = status
        target_state.error = error
        target_state.error_detail = error_detail
        if status in {"success", "failed"}:
            target_state.current_task = None
        self.state_store.save(state)

    def _update_target_progress(self, state: DeploymentState, deployment_name: str, current_task: str) -> None:
        target_state = state.targets.get(deployment_name)
        if not target_state:
            return

        target_state.current_task = current_task
        self.state_store.save(state)
