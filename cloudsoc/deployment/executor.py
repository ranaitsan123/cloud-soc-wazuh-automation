"""Custom YAML deployment executor - replaces Ansible playbook execution."""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml

from cloudsoc.aws.ssm import SSMService
from cloudsoc.utils.shell import run_command, ShellCommandError
from cloudsoc.utils.logger import logger


class DeploymentTask:
    """Represents a single deployment task."""

    def __init__(self, name: str, task_type: str, config: Dict[str, Any]):
        self.name = name
        self.task_type = task_type
        self.config = config

    def execute(self, variables: Dict[str, Any]) -> bool:
        """Execute the task locally."""
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

    def to_shell_commands(self, variables: Dict[str, Any]) -> List[str]:
        """Render the task as shell commands for remote execution."""
        if self.task_type == "shell":
            return [self._substitute_vars(self.config.get("cmd", ""), variables)]
        if self.task_type == "command":
            cmd = self.config.get("cmd")
            if isinstance(cmd, list):
                cmd = " ".join(self._substitute_vars(c, variables) for c in cmd)
            else:
                cmd = self._substitute_vars(str(cmd), variables)
            return [cmd]
        if self.task_type == "package":
            packages = self.config.get("packages")
            if isinstance(packages, str):
                packages = [packages]
            packages = [self._substitute_vars(str(pkg), variables) for pkg in packages or []]
            install_cmd = "sudo apt-get update -y && sudo apt-get install -y"
            if packages:
                install_cmd += " " + " ".join(packages)
            return [install_cmd]
        if self.task_type == "directory":
            paths = self.config.get("paths")
            if isinstance(paths, str):
                paths = [paths]
            paths = [self._substitute_vars(str(path), variables) for path in paths or []]
            commands = []
            for path in paths:
                commands.append(f"sudo mkdir -p {path}")
            mode = self.config.get("mode")
            if mode:
                for path in paths:
                    commands.append(f"sudo chmod {mode} {path}")
            return commands
        if self.task_type == "download":
            source = self._substitute_vars(str(self.config.get("source", "")), variables)
            dest = self._substitute_vars(str(self.config.get("dest", "")), variables)
            if source.startswith("s3://"):
                return [f"aws s3 cp {source} {dest}"]
            return [f"curl -fsSL -o {dest} {source}"]
        if self.task_type == "file":
            action = self.config.get("action", "create")
            path = self._substitute_vars(str(self.config.get("path", "")), variables)
            if action == "create":
                content = self._substitute_vars(str(self.config.get("content", "")), variables)
                return [f"sudo mkdir -p $(dirname {path})", f"cat <<'EOF' | sudo tee {path} > /dev/null\n{content}\nEOF"]
            if action == "delete":
                return [f"sudo rm -f {path}"]
            if action == "append":
                content = self._substitute_vars(str(self.config.get("content", "")), variables)
                return [f"cat <<'EOF' | sudo tee -a {path} > /dev/null\n{content}\nEOF"]
            raise ValueError(f"Unsupported file action: {action}")
        if self.task_type == "service":
            name = self._substitute_vars(str(self.config.get("name", "")), variables)
            state = self.config.get("state", "started")
            commands = []
            if state in ["started", "restarted"]:
                verb = "restart" if state == "restarted" else "start"
                commands.append(f"sudo systemctl {verb} {name}")
            elif state == "stopped":
                commands.append(f"sudo systemctl stop {name}")
            if self.config.get("enabled", False):
                commands.append(f"sudo systemctl enable {name}")
            return commands
        if self.task_type == "docker":
            operation = self.config.get("operation")
            compose_file = self._substitute_vars(str(self.config.get("compose_file", "docker-compose.yml")), variables)
            cwd = self._substitute_vars(str(self.config.get("cwd", "")), variables) if self.config.get("cwd") else None
            if operation == "compose_up":
                cmd = f"cd {cwd} && docker compose -f {compose_file} up -d" if cwd else f"docker compose -f {compose_file} up -d"
                return [cmd]
            if operation == "compose_run":
                service = self._substitute_vars(str(self.config.get("service", "")), variables)
                cmd = f"cd {cwd} && docker compose -f {compose_file} run --rm {service}" if cwd else f"docker compose -f {compose_file} run --rm {service}"
                return [cmd]
            raise ValueError(f"Unsupported docker operation: {operation}")
        raise ValueError(f"Unsupported task type: {self.task_type}")

    def _substitute_vars(self, text: str, variables: Dict[str, Any]) -> str:
        """Replace variables in text using {{ var }} syntax."""
        if not isinstance(text, str):
            return text

        for key, value in variables.items():
            pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
            text = re.sub(pattern, str(value), text)

        return text

    def _execute_shell(self, variables: Dict[str, Any]) -> bool:
        """Execute a shell command locally."""
        cmd = self.config.get("cmd")
        if not cmd:
            logger.error(f"Task '{self.name}': shell command not provided")
            return False

        cmd = self._substitute_vars(str(cmd), variables)
        skip_if_exists = self.config.get("skip_if_exists")

        if skip_if_exists:
            skip_path = self._substitute_vars(str(skip_if_exists), variables)
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
        """Execute a command locally."""
        cmd_list = self.config.get("cmd")
        if not cmd_list:
            logger.error(f"Task '{self.name}': command not provided")
            return False

        if isinstance(cmd_list, str):
            cmd_list = [cmd_list]

        cmd_list = [self._substitute_vars(str(c), variables) for c in cmd_list]
        skip_if_exists = self.config.get("skip_if_exists")

        if skip_if_exists:
            skip_path = self._substitute_vars(str(skip_if_exists), variables)
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
        """Install packages locally."""
        packages = self.config.get("packages")
        if not packages:
            logger.error(f"Task '{self.name}': packages not provided")
            return False

        if isinstance(packages, str):
            packages = [packages]

        packages = [str(p) for p in packages]

        logger.info(f"Running: {self.name}")
        try:
            run_command(["sudo", "apt-get", "update", "-y"], shell=False)
            run_command(["sudo", "apt-get", "install", "-y"] + packages, shell=False)
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_directory(self, variables: Dict[str, Any]) -> bool:
        """Create directories locally."""
        paths = self.config.get("paths")
        if not paths:
            logger.error(f"Task '{self.name}': paths not provided")
            return False

        if isinstance(paths, str):
            paths = [paths]

        paths = [self._substitute_vars(str(path), variables) for path in paths]

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
        """Download files locally."""
        source = self.config.get("source")
        dest = self.config.get("dest")

        if not source or not dest:
            logger.error(f"Task '{self.name}': source or dest not provided")
            return False

        source = self._substitute_vars(str(source), variables)
        dest = self._substitute_vars(str(dest), variables)
        skip_if_exists = self.config.get("skip_if_exists")

        if skip_if_exists:
            skip_path = self._substitute_vars(str(skip_if_exists), variables)
            if Path(skip_path).exists():
                logger.info(f"Task '{self.name}': Skipped (file already exists)")
                return True

        logger.info(f"Running: {self.name}")
        try:
            if source.startswith("s3://"):
                run_command(["aws", "s3", "cp", source, dest], shell=False)
            else:
                run_command(["curl", "-o", dest, source], shell=False)
            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_file(self, variables: Dict[str, Any]) -> bool:
        """Manage files locally."""
        action = self.config.get("action", "create")
        path = self.config.get("path")

        if not path:
            logger.error(f"Task '{self.name}': path not provided")
            return False

        path = self._substitute_vars(str(path), variables)

        logger.info(f"Running: {self.name}")
        try:
            if action == "create":
                content = self._substitute_vars(str(self.config.get("content", "")), variables)
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                Path(path).write_text(content)
            elif action == "delete":
                if Path(path).exists():
                    Path(path).unlink()
            elif action == "append":
                content = self._substitute_vars(str(self.config.get("content", "")), variables)
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
        """Manage services locally."""
        service_name = self.config.get("name")
        state = self.config.get("state", "started")
        enabled = self.config.get("enabled", False)

        if not service_name:
            logger.error(f"Task '{self.name}': service name not provided")
            return False

        logger.info(f"Running: {self.name}")
        try:
            if state in ["started", "restarted"]:
                cmd = "restart" if state == "restarted" else "start"
                run_command(["sudo", "systemctl", cmd, service_name], shell=False)
            elif state == "stopped":
                run_command(["sudo", "systemctl", "stop", service_name], shell=False)

            if enabled:
                run_command(["sudo", "systemctl", "enable", service_name], shell=False)

            return True
        except ShellCommandError as e:
            logger.error(f"Task '{self.name}' failed: {e}")
            return False

    def _execute_docker(self, variables: Dict[str, Any]) -> bool:
        """Manage Docker locally."""
        operation = self.config.get("operation")
        if not operation:
            logger.error(f"Task '{self.name}': operation not provided")
            return False

        logger.info(f"Running: {self.name}")
        try:
            compose_file = self._substitute_vars(str(self.config.get("compose_file", "docker-compose.yml")), variables)
            cwd = self._substitute_vars(str(self.config.get("cwd", "")), variables) if self.config.get("cwd") else None

            if operation == "compose_up":
                cmd = ["docker", "compose", "-f", compose_file, "up", "-d"]
            elif operation == "compose_run":
                service = self._substitute_vars(str(self.config.get("service", "")), variables)
                cmd = ["docker", "compose", "-f", compose_file, "run", "--rm", service]
            else:
                logger.error(f"Task '{self.name}': unknown operation {operation}")
                return False

            run_command(cmd, shell=False, cwd=cwd)
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
        return [DeploymentTask(task.get("name", "unnamed"), task.get("type", "shell"), task) for task in tasks_list]

    def execute(
        self,
        variables: Optional[Dict[str, Any]] = None,
        ssm_service: Optional[SSMService] = None,
        instance_ids: Optional[List[str]] = None,
    ) -> bool:
        """Execute all tasks in the plan either locally or remotely via SSM."""
        variables = variables or {}
        logger.info(f"Starting deployment: {self.name}")

        if ssm_service and instance_ids:
            return self._execute_remote(variables, ssm_service, instance_ids)

        for task in self.tasks:
            if not task.execute(variables):
                logger.error(f"Deployment failed at task: {task.name}")
                return False

        logger.info(f"✓ Deployment completed: {self.name}")
        return True

    def _execute_remote(
        self,
        variables: Dict[str, Any],
        ssm_service: SSMService,
        instance_ids: List[str]
    ) -> bool:
        """Execute the deployment remotely via SSM."""
        commands: List[str] = ["set -e"]

        for task in self.tasks:
            try:
                task_commands = task.to_shell_commands(variables)
            except Exception as e:
                logger.error(f"Unable to render task '{task.name}' for remote execution: {e}")
                return False

            if not task_commands:
                continue

            commands.append(f"echo 'Running task: {task.name}'")
            commands.extend(task_commands)

        script = "\n".join(commands)
        command_id = ssm_service.send_command(
            instance_ids=instance_ids,
            commands=[script],
            working_directory="/tmp",
            timeout=3600,
            document_name="AWS-RunShellScript"
        )

        if not command_id:
            logger.error("SSM remote deployment failed to send command")
            return False

        for instance_id in instance_ids:
            invocation = ssm_service.wait_for_command(command_id, instance_id, timeout=3600, poll_interval=10)
            if not invocation:
                logger.error(f"SSM remote deployment did not complete for {instance_id}")
                return False
            if invocation.get("status") != "Success" or invocation.get("return_code") != 0:
                logger.error(
                    f"SSM remote deployment failed on {instance_id}: status={invocation.get('status')} return_code={invocation.get('return_code')}"
                )
                logger.error(invocation.get("error", ""))
                return False

        logger.info(f"✓ Remote deployment completed: {self.name}")
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
        variables: Optional[Dict[str, Any]] = None,
        ssm_service: Optional[SSMService] = None,
        instance_ids: Optional[List[str]] = None,
    ) -> bool:
        """
        Run a deployment from a YAML file.

        Args:
            deployment_name: Name of the deployment file (without .yml)
            variables: Variables to substitute in the deployment
            ssm_service: Optional SSM service for remote execution
            instance_ids: Optional list of target instance IDs

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
            return plan.execute(
                variables=variables or {},
                ssm_service=ssm_service,
                instance_ids=instance_ids,
            )

        except Exception as e:
            self.logger.error(f"Failed to load deployment: {e}")
            return False
