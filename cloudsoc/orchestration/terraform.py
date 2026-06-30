from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.terraform.imports import ResourceImporter
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError
from cloudsoc.models.outputs import InfrastructureOutputs
from cloudsoc.utils.logger import logger
from cloudsoc.orchestration.errors import OrchestrationError


class TerraformOrchestrator:
    """Manages Terraform infrastructure lifecycle operations."""

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

    def init(self) -> None:
        self.tf_runner.init()

    def import_all_existing_resources(self, var_files: Optional[List[str]] = None) -> None:
        try:
            importer = ResourceImporter(
                tf_runner=self.tf_runner,
                settings=self.settings,
            )
            importer.import_all_existing_resources(var_files=var_files)
            logger.info("✓ Resource import check completed")
        except Exception as e:
            logger.warning(f"Resource import encountered an issue (non-critical): {e}")
            logger.info("Proceeding with deployment - Terraform will handle creation of missing resources")

    def validate(self) -> None:
        self.tf_runner.validate()

    def plan(self, var_files: Optional[List[str]] = None) -> str:
        return self.tf_runner.plan(var_files=var_files or [])

    def apply(self, plan_file: str, auto_approve: bool = False) -> None:
        self.tf_runner.apply(plan_file=plan_file, auto_approve=auto_approve)

    def destroy(self, auto_approve: bool = False) -> None:
        self.tf_runner.destroy(auto_approve=auto_approve)

    def output(self) -> InfrastructureOutputs:
        outputs = self.tf_runner.output()
        if outputs is None:
            raise OrchestrationError("No Terraform outputs could be retrieved.")
        return InfrastructureOutputs.from_terraform_outputs(outputs)

    def raw_output(self) -> Dict[str, Any]:
        return self.tf_runner.output()
