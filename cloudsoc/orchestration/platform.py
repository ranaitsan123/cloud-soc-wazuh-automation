from __future__ import annotations

from typing import List, Optional

from cloudsoc.config.settings import get_settings
from cloudsoc.orchestration.build import BuildOrchestrator
from cloudsoc.orchestration.dashboard import DashboardOrchestrator
from cloudsoc.orchestration.deployment import DeploymentOrchestrator
from cloudsoc.orchestration.errors import OrchestrationError
from cloudsoc.orchestration.terraform import TerraformOrchestrator
from cloudsoc.models.outputs import InfrastructureOutputs


class PlatformOrchestrator:
    def __init__(self):
        self.settings = get_settings()
        self.terraform = TerraformOrchestrator(settings=self.settings)
        self.deployment = DeploymentOrchestrator(settings=self.settings)
        self.dashboard = DashboardOrchestrator(settings=self.settings)
        self.build = BuildOrchestrator(settings=self.settings)

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
        self.terraform.import_all_existing_resources()
        self.terraform.validate()
        plan_file = self.terraform.plan(var_files=var_files)
        self.terraform.apply(plan_file=plan_file, auto_approve=auto_approve)

    def deploy(
        self,
        targets: Optional[List[str]] = None,
        skip_validation: bool = False,
    ) -> InfrastructureOutputs:
        outputs = self.terraform.output()
        if not outputs.raw:
            raise OrchestrationError("No Terraform outputs found. Run 'cloud-soc apply' first.")

        instance_ids = [id for id in [outputs.wazuh_instance_id, outputs.victim_instance_id] if id]
        self.deployment.wait_for_ssm_ready(instance_ids)
        self.deployment.deploy_targets(outputs, targets=targets, skip_validation=skip_validation)

        if not skip_validation:
            self.deployment.validate_deployment(outputs)

        return outputs

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
