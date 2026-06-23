from __future__ import annotations

import re
from typing import List, Optional

from cloudsoc.aws.ecr import ECRService
from cloudsoc.config.settings import Settings, get_settings
from cloudsoc.utils.logger import logger
from cloudsoc.utils.shell import ShellCommandError, run_command
from cloudsoc.orchestration.errors import OrchestrationError


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

        command = [
            "gh",
            "workflow",
            "run",
            workflow_file,
            "--ref",
            ref or self._get_current_branch(),
        ]

        try:
            result = run_command(command, capture_output=True)
            output = (result.stdout or "") + (result.stderr or "")
            workflow_run_id = self._parse_workflow_run_id(output)

            logger.info(f"Triggered GitHub workflow {workflow_file} for target {target}. run id={workflow_run_id}")

            if wait:
                run_command(["gh", "run", "watch", workflow_run_id, "--exit-status"])
        except ShellCommandError as e:
            raise OrchestrationError(f"Failed to trigger build workflow for {target}: {e}") from e

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

    def _get_current_branch(self) -> str:
        try:
            result = run_command(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
            )
            branch = (result.stdout or "").strip()
            if not branch or branch == "HEAD":
                raise OrchestrationError(
                    "Unable to determine current git branch for workflow ref."
                )
            return branch
        except ShellCommandError as e:
            raise OrchestrationError(
                f"Unable to determine current git branch: {e}"
            ) from e
