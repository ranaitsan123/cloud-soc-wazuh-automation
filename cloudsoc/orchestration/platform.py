from __future__ import annotations

from typing import List, Optional

from cloudsoc.config.settings import get_settings
from cloudsoc.orchestration.build import BuildOrchestrator
from cloudsoc.orchestration.dashboard import DashboardOrchestrator
from cloudsoc.orchestration.deployment import DeploymentOrchestrator
from cloudsoc.orchestration.errors import OrchestrationError
from cloudsoc.orchestration.terraform import TerraformOrchestrator
from cloudsoc.aws.s3 import S3Service
from cloudsoc.models.outputs import InfrastructureOutputs
from cloudsoc.utils.logger import logger


class PlatformOrchestrator:
    def __init__(self):
        self.settings = get_settings()
        self.terraform = TerraformOrchestrator(settings=self.settings)
        self.deployment = DeploymentOrchestrator(settings=self.settings)
        self.dashboard = DashboardOrchestrator(settings=self.settings)
        self.build = BuildOrchestrator(settings=self.settings)
        self.s3_service = S3Service(
            region=self.settings.project.aws.region,
            profile=self.settings.project.aws.profile,
        )

    def up(
        self,
        build_flag: bool = False,
        auto_approve: bool = False,
        skip_validation: bool = False,
    ) -> InfrastructureOutputs:
        self.terraform.init()
        self.terraform.import_all_existing_resources()
        self.terraform.validate()
        plan_file = self.terraform.plan()
        self.terraform.apply(plan_file=plan_file, auto_approve=auto_approve)
        self.upload_assets()

        if build_flag:
            self.build.build_targets(wait=True)

        outputs = self.terraform.output()

        instance_ids = [id for id in [outputs.wazuh_instance_id, outputs.victim_instance_id] if id]
        self.deployment.wait_for_ssm_ready(instance_ids)
        self.deployment.deploy_targets(outputs, targets=None, skip_validation=skip_validation)

        if not skip_validation:
            self.deployment.validate_deployment(outputs)

        return outputs

    def apply(self, auto_approve: bool = False, var_files: Optional[List[str]] = None) -> None:
        self.terraform.init()
        self.terraform.import_all_existing_resources(var_files=var_files)
        self.terraform.validate()
        plan_file = self.terraform.plan(var_files=var_files)
        self.terraform.apply(plan_file=plan_file, auto_approve=auto_approve)
        self.upload_assets()

    def upload_assets(self) -> int:
        """Upload local S3 assets into the provisioned bucket."""
        outputs = self.terraform.output()
        if not outputs.raw:
            raise OrchestrationError("No Terraform outputs found. Run 'cloud-soc apply' first.")

        bucket_name = outputs.s3_bucket_name
        if not bucket_name:
            raise OrchestrationError("Terraform did not produce an S3 bucket output.")

        s3_prefix = outputs.s3_prefix or "wazuh-docker"
        uploaded_count = self.s3_service.upload_assets(bucket=bucket_name, s3_prefix=s3_prefix)

        if uploaded_count == 0:
            logger.warning("No asset files were uploaded to S3. Check that wazuh-docker and atomics directories exist.")
        else:
            logger.info(f"Uploaded {uploaded_count} asset files to S3 bucket {bucket_name}")

        return uploaded_count

    def deploy(
        self,
        targets: Optional[List[str]] = None,
        skip_validation: bool = False,
    ) -> InfrastructureOutputs:
        outputs = self.terraform.output()
        if not outputs.raw:
            raise OrchestrationError("No Terraform outputs found. Run 'cloud-soc apply' first.")

        deployment_targets = self._resolve_deployment_targets(targets)
        instance_ids = self._resolve_instance_ids(outputs, deployment_targets)
        self.deployment.wait_for_ssm_ready(instance_ids)
        self.deployment.deploy_targets(outputs, targets=targets, skip_validation=skip_validation)

        if not skip_validation:
            self.deployment.validate_deployment(outputs)

        return outputs

    def _resolve_deployment_targets(self, targets: Optional[List[str]]) -> List[str]:
        if not targets:
            return ["wazuh_manager", "victim_server"]

        resolved_targets: List[str] = []
        for target in targets:
            normalized_target = target.strip().lower()
            if normalized_target in {"wazuh", "wazuh_manager"}:
                resolved_targets.append("wazuh_manager")
            elif normalized_target in {"victim", "victim_server"}:
                resolved_targets.append("victim_server")
            else:
                resolved_targets.append(target)

        return resolved_targets

    def _resolve_instance_ids(self, outputs: InfrastructureOutputs, targets: List[str]) -> List[str]:
        instance_ids: List[str] = []
        if "wazuh_manager" in targets and outputs.wazuh_instance_id:
            instance_ids.append(outputs.wazuh_instance_id)
        if "victim_server" in targets and outputs.victim_instance_id:
            instance_ids.append(outputs.victim_instance_id)
        return instance_ids

    def open_dashboard_tunnel(
        self,
        local_port: int = 8443,
        remote_port: int = 443,
        expose: bool = False,
    ) -> None:
        outputs = self.terraform.output()
        if not outputs:
            raise OrchestrationError("No Terraform outputs found. Run 'cloud-soc apply' first.")

        self.dashboard.open_tunnel(outputs, local_port=local_port, remote_port=remote_port, expose=expose)

    def dashboard_status(self) -> dict[str, object]:
        return self.dashboard.status()
