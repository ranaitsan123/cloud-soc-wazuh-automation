"""Custom YAML deployment executor - replaces Ansible playbook execution."""

import os
import re
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml
import subprocess

from cloudsoc.utils.shell import run_command, ShellCommandError
from cloudsoc.utils.logger import logger


class DeploymentTask:
    """Represents a single deployment task."""

    def __init__(self, name: str, task_type: str, config: Dict[str, Any]):
        self.name = name
        self.task_type = task_type
        self.config = config

    def execute(self, variables: Dict[str, Any]) -> bool:
        """Execute the task with given variables."""
        try:
            if self.task_type == "shell":
                return self._execute_shell(variables)
            elif self.task_type == "command":
                return self._execute_command(variables)
            elif self.task_type == "package":
                return self._execute_package(variables)
            elif self.task_type == "directory":
                return self._execute_directory(variables)
            elif self.task_type == "download":
                return self._execute_download(variables)
            elif self.task_type == "file":
                return self._execute_file(variables)
            elif self.task_type == "service":
                return self._execute_service(variables)
            elif self.task_type == "docker":
                return self._execute_docker(variables)
            else:
                logger.error(f"Unknown task type: {self.task_type}")
                return False
        except Exception as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _substitute_vars(self, text: str, variables: Dict[str, Any]) -> str:
        """Replace variables in text using {{ var }} syntax."""
        if not isinstance(text, str):
            return text

        for key, value in variables.items():
            pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
            text = re.sub(pattern, str(value), text)

        return text

    def _substitute_vars_recursive(self, obj: Any, variables: Dict[str, Any]) -> Any:
        """Recursively substitute variables in objects."""
        if isinstance(obj, str):
            return self._substitute_vars(obj, variables)
        elif isinstance(obj, dict):
            return {k: self._substitute_vars_recursive(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_vars_recursive(item, variables) for item in obj]
        else:
            return obj

    def _execute_shell(self, variables: Dict[str, Any]) -> bool:
        """Execute a shell command."""
        cmd = self.config.get("cmd")
        if not cmd:
            logger.error(f"Task '{self.name}': shell command not provided")
            return False

        cmd = self._substitute_vars(cmd, variables)
        skip_if_exists = self.config.get("skip_if_exists")

        if skip_if_exists:
            skip_path = self._substitute_vars(skip_if_exists, variables)
            if Path(skip_path).exists():
                logger.info(f"Task '{self.name}': Skipped (condition met)")
                return True

        logger.info(f"Running: {self.name}")
        try:
            run_command(cmd, shell=True)
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_command(self, variables: Dict[str, Any]) -> bool:
        """Execute a command (non-shell)."""
        cmd_list = self.config.get("cmd")
        if not cmd_list:
            logger.error(f"Task '{self.name}': command not provided")
            return False

        if isinstance(cmd_list, str):
            cmd_list = [cmd_list]

        cmd_list = [self._substitute_vars(c, variables) for c in cmd_list]
        skip_if_exists = self.config.get("skip_if_exists")

        if skip_if_exists:
            skip_path = self._substitute_vars(skip_if_exists, variables)
            if Path(skip_path).exists():
                logger.info(f"Task '{self.name}': Skipped (condition met)")
                return True

        logger.info(f"Running: {self.name}")
        try:
            run_command(cmd_list)
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_package(self, variables: Dict[str, Any]) -> bool:
        """Install packages using apt."""
        packages = self.config.get("packages")
        if not packages:
            logger.error(f"Task '{self.name}': packages not provided")
            return False

        if isinstance(packages, str):
            packages = [packages]

        logger.info(f"Running: {self.name}")
        try:
            run_command(["sudo", "apt-get", "update"], shell=False)
            run_command(["sudo", "apt-get", "install", "-y"] + packages, shell=False)
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_directory(self, variables: Dict[str, Any]) -> bool:
        """Create directories."""
        paths = self.config.get("paths")
        if not paths:
            logger.error(f"Task '{self.name}': paths not provided")
            return False

        if isinstance(paths, str):
            paths = [paths]

        paths = [self._substitute_vars(p, variables) for p in paths]

        logger.info(f"Running: {self.name}")
        try:
            for path in paths:
                Path(path).mkdir(parents=True, exist_ok=True)
                mode = self.config.get("mode")
                if mode:
                    os.chmod(path, int(mode, 8))
            return True
        except Exception as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_download(self, variables: Dict[str, Any]) -> bool:
        """Download files from S3 or HTTP."""
        source = self.config.get("source")
        dest = self.config.get("dest")

        if not source or not dest:
            logger.error(f"Task '{self.name}': source or dest not provided")
            return False

        source = self._substitute_vars(source, variables)
        dest = self._substitute_vars(dest, variables)
        skip_if_exists = self.config.get("skip_if_exists")

        if skip_if_exists:
            skip_path = self._substitute_vars(skip_if_exists, variables)
            if Path(skip_path).exists():
                logger.info(f"Task '{self.name}': Skipped (file already exists)")
                return True

        logger.info(f"Running: {self.name}")
        try:
            if source.startswith("s3://"):
                # Use aws s3 cp for S3 downloads
                run_command(["aws", "s3", "cp", source, dest], shell=False)
            else:
                # Use curl for HTTP downloads
                run_command(["curl", "-o", dest, source], shell=False)
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_file(self, variables: Dict[str, Any]) -> bool:
        """Manage file operations."""
        action = self.config.get("action", "create")
        path = self.config.get("path")

        if not path:
            logger.error(f"Task '{self.name}': path not provided")
            return False

        path = self._substitute_vars(path, variables)

        logger.info(f"Running: {self.name}")
        try:
            if action == "create":
                content = self.config.get("content", "")
                content = self._substitute_vars(content, variables)
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).write_text(content)
            elif action == "delete":
                if Path(path).exists():
                    Path(path).unlink()
            elif action == "append":
                content = self.config.get("content", "")
                content = self._substitute_vars(content, variables)
                with open(path, "a") as f:
                    f.write(content)
            else:
                logger.error(f"Task '{self.name}': unknown action {action}")
                return False
            return True
        except Exception as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_service(self, variables: Dict[str, Any]) -> bool:
        """Manage system services."""
        service_name = self.config.get("name")
        state = self.config.get("state", "started")  # started, stopped, restarted
        enabled = self.config.get("enabled", False)

        if not service_name:
            logger.error(f"Task '{self.name}': service name not provided")
            return False

        logger.info(f"Running: {self.name}")
        try:
            if state in ["started", "restarted"]:
                cmd = "restart" if state == "restarted" else "start"
                run_command(["sudo", "systemctl", cmd, service_name], shell=False)

            if enabled:
                run_command(["sudo", "systemctl", "enable", service_name], shell=False)

            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_docker(self, variables: Dict[str, Any]) -> bool:
        """Execute Docker operations."""
        operation = self.config.get("operation")
        if not operation:
            logger.error(f"Task '{self.name}': operation not provided")
            return False

        logger.info(f"Running: {self.name}")
        try:
            if operation == "compose_up":
                cwd = self.config.get("cwd")
                compose_file = self.config.get("compose_file", "docker-compose.yml")
                compose_file = self._substitute_vars(compose_file, variables)
                cwd = self._substitute_vars(cwd, variables) if cwd else None
                run_command(
                    ["docker", "compose", "-f", compose_file, "up", "-d"],
                    shell=False,
                    cwd=cwd
                )
            elif operation == "compose_run":
                cwd = self.config.get("cwd")
                compose_file = self.config.get("compose_file", "docker-compose.yml")
                service = self.config.get("service")
                compose_file = self._substitute_vars(compose_file, variables)
                service = self._substitute_vars(service, variables)
                cwd = self._substitute_vars(cwd, variables) if cwd else None
                run_command(
                    ["docker", "compose", "-f", compose_file, "run", "--rm", service],
                    shell=False,
                    cwd=cwd
                )
            else:
                logger.error(f"Task '{self.name}': unknown operation {operation}")
                return False
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False


class DeploymentPlan:
    """Represents a deployment plan from YAML."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "deployment")
        self.description = config.get("description", "")
        self.tasks = self._parse_tasks(config.get("tasks", []))

    def _parse_tasks(self, tasks_list: List[Dict[str, Any]]) -> List[DeploymentTask]:
        """Parse task definitions from YAML."""
        tasks = []
        for task_config in tasks_list:
            name = task_config.get("name", "unnamed")
            task_type = task_config.get("type", "shell")
            task = DeploymentTask(name, task_type, task_config)
            tasks.append(task)
        return tasks

    def execute(self, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Execute all tasks in the plan."""
        variables = variables or {}
        logger.info(f"Starting deployment: {self.name}")

        for task in self.tasks:
            success = task.execute(variables)
            if not success:
                logger.error(f"Deployment failed at task: {task.name}")
                return False

        logger.info(f"✓ Deployment completed: {self.name}")
        return True


class DeploymentService:
    """Service for custom YAML-based deployment execution."""

    def __init__(self, deployment_dir: Path = Path("deployment")):
        """
        Initialize deployment service.

        Args:
            deployment_dir: Path to deployment definitions directory
        """
        self.deployment_dir = Path(deployment_dir)
        self.logger = logger

    def run_deployment(
        self,
        deployment_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Run a deployment from a YAML file.

        Args:
            deployment_name: Name of the deployment file (without .yml)
            variables: Variables to substitute in the deployment

        Returns:
            True if successful
        """
        deployment_path = self.deployment_dir / f"{deployment_name}.yml"

        if not deployment_path.exists():
            self.logger.error(f"Deployment file not found: {deployment_path}")
            return False

        try:
            with open(deployment_path, "r") as f:
                config = yaml.safe_load(f)

            if not config:
                self.logger.error(f"Empty deployment file: {deployment_path}")
                return False

            plan = DeploymentPlan(config)
            return plan.execute(variables or {})

        except Exception as e:
            self.logger.error(f"Failed to load deployment: {e}")
            return False
