"""Terraform runner and orchestration"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.syntax import Syntax
from cloudsoc.utils.shell import run_command, ShellCommandError
from cloudsoc.utils.logger import logger
from cloudsoc.utils.retry import retry


console = Console()


class TerraformStateError(Exception):
    """Raised when Terraform state operations fail"""
    pass


class TerraformRunner:
    """
    Orchestrates Terraform operations safely.

    Wraps subprocess calls with logging, error handling, and state management.
    """

    def __init__(
        self,
        terraform_dir: Path,
        auto_approve: bool = False,
        backend_config: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize Terraform runner.

        Args:
            terraform_dir: Path to Terraform directory
            auto_approve: Automatically approve apply operations
            backend_config: Optional Terraform backend configuration values
        """
        self.terraform_dir = Path(terraform_dir)
        self.auto_approve = auto_approve
        self.backend_config = backend_config or {}

        if not self.terraform_dir.exists():
            raise ValueError(f"Terraform directory not found: {terraform_dir}")

    def init(self, upgrade: bool = False) -> None:
        """
        Run terraform init.

        Args:
            upgrade: Upgrade Terraform state to latest version
        """
        logger.info(f"[terraform init] in {self.terraform_dir}")

        cmd = ["terraform", "init", "-input=false"]
        if upgrade:
            cmd.append("-upgrade")

        backend_override_path = self.terraform_dir / ".backend_override.tf"
        use_s3_backend = bool(
            self.backend_config.get("bucket") and self.backend_config.get("key")
        )

        if use_s3_backend:
            backend_override_path.write_text(
                'terraform {\n  backend "s3" {}\n}\n'
            )
        elif backend_override_path.exists():
            backend_override_path.unlink()

        if self.backend_config:
            if any(
                self.backend_config.get(k)
                for k in ["bucket", "key", "region", "dynamodb_table"]
            ) and not use_s3_backend:
                logger.error(
                    "Terraform backend config is incomplete: set TERRAFORM_BACKEND_BUCKET and TERRAFORM_BACKEND_KEY."
                )
                raise TerraformStateError(
                    "Terraform backend config is missing required values: bucket and key."
                )

        if use_s3_backend:
            for key, value in self.backend_config.items():
                if value:
                    cmd.extend(["-backend-config", f"{key}={value}"])

        try:
            self._run(cmd)
            logger.info("✓ Terraform initialized")
        except ShellCommandError as e:
            logger.error(f"✗ Terraform init failed: {e}")
            raise TerraformStateError(f"Failed to initialize Terraform: {e}") from e

    def validate(self) -> None:
        """Validate Terraform configuration."""
        logger.info("[terraform validate]")

        try:
            self._run(["terraform", "validate", "-json"])
            logger.info("✓ Terraform configuration is valid")
        except ShellCommandError as e:
            logger.error(f"✗ Validation failed: {e}")
            raise TerraformStateError(f"Terraform validation failed: {e}") from e

    def plan(
        self,
        out: str = "tfplan",
        var_files: Optional[List[str]] = None,
        targets: Optional[List[str]] = None,
        destroy: bool = False
    ) -> str:
        """
        Run terraform plan.

        Args:
            out: Output file for the plan
            var_files: Additional variable files
            targets: Specific resources to target
            destroy: Create a destroy plan

        Returns:
            Path to the plan file
        """
        logger.info("[terraform plan]")

        cmd = ["terraform", "plan", "-input=false"]

        if destroy:
            cmd.append("-destroy")

        if var_files:
            for var_file in var_files:
                cmd.extend(["-var-file", var_file])

        if targets:
            for target in targets:
                cmd.extend(["-target", target])

        cmd.extend(["-out", out])

        try:
            self._run(cmd)
            logger.info(f"✓ Plan saved to {out}")
            return out
        except ShellCommandError as e:
            logger.error(f"✗ Plan failed: {e}")
            raise TerraformStateError(f"Terraform plan failed: {e}") from e

    def apply(
        self,
        plan_file: Optional[str] = None,
        auto_approve: Optional[bool] = None
    ) -> None:
        """
        Run terraform apply.

        Args:
            plan_file: Path to plan file (if None, creates and applies in one step)
            auto_approve: Override instance setting for auto-approval
        """
        logger.info("[terraform apply]")

        approve = auto_approve if auto_approve is not None else self.auto_approve

        cmd = ["terraform", "apply", "-input=false"]

        if approve:
            cmd.append("-auto-approve")

        if plan_file:
            cmd.append(plan_file)

        try:
            self._run(cmd)
            logger.info("✓ Infrastructure applied successfully")
        except ShellCommandError as e:
            logger.error(f"✗ Apply failed: {e}")
            raise TerraformStateError(f"Terraform apply failed: {e}") from e

    def destroy(self, auto_approve: Optional[bool] = None) -> None:
        """
        Run terraform destroy.

        Args:
            auto_approve: Override instance setting for auto-approval
        """
        logger.warning("[terraform destroy]")

        approve = auto_approve if auto_approve is not None else self.auto_approve

        cmd = ["terraform", "destroy", "-input=false"]

        if approve:
            cmd.append("-auto-approve")

        try:
            self._run(cmd)
            logger.info("✓ Infrastructure destroyed successfully")
        except ShellCommandError as e:
            logger.error(f"✗ Destroy failed: {e}")
            raise TerraformStateError(f"Terraform destroy failed: {e}") from e

    def import_resource(self, address: str, resource_id: str) -> None:
        """
        Import existing AWS resource into Terraform state.

        Args:
            address: Terraform resource address (e.g., aws_vpc.main)
            resource_id: AWS resource ID to import

        Raises:
            TerraformStateError: If import fails
        """
        logger.info(f"[terraform import] {address} <- {resource_id}")

        cmd = ["terraform", "import", "-input=false", address, resource_id]

        try:
            self._run(cmd)
            logger.info(f"✓ Imported {address}")
        except ShellCommandError as e:
            # Import might fail if resource is already in state
            if "already exists in state" in str(e):
                logger.info(f"ℹ Resource {address} already in state")
            else:
                logger.error(f"✗ Import failed: {e}")
                raise TerraformStateError(f"Failed to import {address}: {e}") from e

    def output(self, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Terraform outputs.

        Args:
            key: Specific output key (if None, returns all)

        Returns:
            Dictionary of outputs
        """
        import json

        cmd = ["terraform", "output", "-json"]
        if key:
            cmd.append(key)

        try:
            result = self._run(cmd, capture_output=True)
            return json.loads(result.stdout)
        except (ShellCommandError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to read outputs: {e}")
            return {}

    def output_raw(self, key: str) -> str:
        """Get a Terraform output value in raw format."""
        cmd = ["terraform", "output", "-raw", key]

        try:
            result = self._run(cmd, capture_output=True)
            return result.stdout.strip()
        except ShellCommandError as e:
            logger.warning(f"Failed to read raw output {key}: {e}")
            return ""

    def output_value(self, key: str) -> Any:
        """Get a Terraform output value by key."""
        outputs = self.output()
        return outputs.get(key, {}).get("value")

    def state_contains(self, address: str) -> bool:
        """Return whether a Terraform state contains the given resource address."""
        try:
            result = self._run(["terraform", "state", "list"], capture_output=True)
            return address in result.stdout.splitlines()
        except ShellCommandError as e:
            logger.warning(f"Failed to inspect Terraform state for {address}: {e}")
            return False

    def show_state(self) -> None:
        """Display current Terraform state (for debugging)."""
        logger.info("[terraform show]")
        self._run(["terraform", "show"])

    def _run(
        self,
        cmd: List[str],
        capture_output: bool = False
    ) -> Any:
        """
        Execute Terraform command in the Terraform directory.

        Args:
            cmd: Command to run
            capture_output: Capture stdout/stderr

        Returns:
            CompletedProcess result

        Raises:
            ShellCommandError: If command fails
        """
        console.print(f"[cyan]▶[/cyan] {' '.join(cmd)}")
        return run_command(cmd, cwd=str(self.terraform_dir), capture_output=capture_output)
