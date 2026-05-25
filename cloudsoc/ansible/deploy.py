"""Ansible deployment service"""

import os
from pathlib import Path
from typing import Optional, List
import shutil
from cloudsoc.utils.shell import run_command, ShellCommandError
from cloudsoc.utils.logger import logger


class AnsibleService:
    """Service for Ansible playbook execution"""

    def __init__(self, playbooks_dir: Path = Path("ansible/playbooks")):
        """
        Initialize Ansible service.

        Args:
            playbooks_dir: Path to Ansible playbooks directory
        """
        self.playbooks_dir = Path(playbooks_dir)
        self.roles_path = self.playbooks_dir.parent / "roles"
        self.requirements_file = self.playbooks_dir.parent / "requirements.yml"
        self.logger = logger
        self._collections_installed = False

    def run_playbook(
        self,
        playbook_name: str,
        inventory: Optional[str] = None,
        extra_vars: Optional[dict] = None,
        tags: Optional[List[str]] = None,
        check: bool = False
    ) -> bool:
        """
        Run an Ansible playbook.

        Args:
            playbook_name: Name of the playbook file
            inventory: Inventory file or host pattern
            extra_vars: Extra variables to pass
            tags: Tags to run specific tasks
            check: Run in check mode (dry-run)

        Returns:
            True if successful
        """
        # Ensure collections are installed before running playbooks
        if not self._collections_installed:
            if not self._install_collections():
                return False

        playbook_path = self.playbooks_dir / playbook_name

        if not playbook_path.exists():
            self.logger.error(f"Playbook not found: {playbook_path}")
            return False

        ansible_playbook = self._resolve_ansible_playbook()
        if not ansible_playbook:
            self.logger.error(
                "ansible-playbook was not found on PATH. "
                "Install Ansible or ensure ansible-playbook is available."
            )
            return False

        cmd = [ansible_playbook, str(playbook_path)]

        if inventory:
            cmd.extend(["-i", inventory])

        env = os.environ.copy()

        ansible_config = Path("ansible.cfg")
        if ansible_config.exists():
            env["ANSIBLE_CONFIG"] = str(ansible_config.resolve())

        if self.roles_path.exists():
            env["ANSIBLE_ROLES_PATH"] = str(self.roles_path)

        if extra_vars:
            for key, value in extra_vars.items():
                cmd.extend(["-e", f"{key}={value}"])

        if tags:
            cmd.extend(["--tags", ",".join(tags)])

        if check:
            cmd.append("--check")

        try:
            self.logger.info(f"Running playbook: {playbook_name}")
            run_command(cmd, env=env)
            self.logger.info(f"✓ Playbook {playbook_name} completed successfully")
            return True

        except ShellCommandError as e:
            self.logger.error(f"✗ Playbook failed: {e}")
            return False

    def _resolve_ansible_playbook(self) -> Optional[str]:
        """Resolve the ansible-playbook executable path."""
        return shutil.which("ansible-playbook")

    def _install_collections(self) -> bool:
        """Install Ansible collections from requirements.yml."""
        if not self.requirements_file.exists():
            self.logger.debug(f"No requirements file found at {self.requirements_file}")
            self._collections_installed = True
            return True

        ansible_galaxy = shutil.which("ansible-galaxy")
        if not ansible_galaxy:
            self.logger.error(
                "ansible-galaxy not found. Cannot install required collections. "
                "Install Ansible or ensure ansible-galaxy is available."
            )
            return False

        try:
            self.logger.info("Installing Ansible collections...")
            cmd = [ansible_galaxy, "collection", "install", "-r", str(self.requirements_file)]
            run_command(cmd)
            self.logger.debug("✓ Ansible collections installed successfully")
            self._collections_installed = True
            return True
        except ShellCommandError as e:
            self.logger.error(f"Failed to install Ansible collections: {e}")
            return False


    def run_task(
        self,
        hosts: str,
        module: str,
        args: Optional[str] = None,
        become: bool = False
    ) -> bool:
        """
        Run an Ansible ad-hoc task.

        Args:
            hosts: Host pattern to target
            module: Ansible module to run
            args: Module arguments
            become: Use sudo/become

        Returns:
            True if successful
        """
        cmd = ["ansible", hosts, "-m", module]

        if args:
            cmd.extend(["-a", args])

        if become:
            cmd.append("-b")

        try:
            self.logger.info(f"Running ad-hoc task on {hosts}: {module}")
            run_command(cmd)
            self.logger.info("✓ Task completed successfully")
            return True

        except ShellCommandError as e:
            self.logger.error(f"✗ Task failed: {e}")
            return False
