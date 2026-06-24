import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml

from cloudsoc.aws.ssm import SSMService

DEFAULT_SCENARIOS_FILE = Path("/opt/fortress/atomics/scenarios.yml")


class AtomicRunner:

    def __init__(
        self,
        scenarios_file: Optional[Path] = None,
        ssm_service: Optional[SSMService] = None,
        instance_ids: Optional[List[str]] = None,
    ) -> None:
        if scenarios_file is not None:
            self.scenarios_file = Path(scenarios_file)
        else:
            self.scenarios_file = Path(os.getenv("ATOMICS_SCENARIOS_FILE", DEFAULT_SCENARIOS_FILE))

        self.ssm_service = ssm_service
        self.instance_ids = instance_ids or []

    def list(self) -> Dict[str, Any]:
        if not self.scenarios_file.exists():
            raise FileNotFoundError(f"Scenarios file not found: {self.scenarios_file}")

        data = yaml.safe_load(self.scenarios_file.read_text()) or {}
        return data.get("scenarios", {})

    def run(
        self,
        technique_id: str,
        timeout: int = 3600,
    ) -> subprocess.CompletedProcess[str]:
        scenarios = self.list()
        if technique_id not in scenarios:
            raise ValueError(f"Unknown technique: {technique_id}")

        cmd = scenarios[technique_id].get("command")
        if not cmd:
            raise ValueError(f"No command defined for technique: {technique_id}")

        if not self.ssm_service or not self.instance_ids:
            raise RuntimeError(
                "Remote atomic execution requires an SSM service and at least one victim instance ID"
            )

        return self._run_remote(cmd, timeout=timeout)

    def _run_local(self, cmd: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True,
        )

    def _run_remote(self, cmd: str, timeout: int = 3600) -> subprocess.CompletedProcess[str]:
        command_id = self.ssm_service.send_command(
            instance_ids=self.instance_ids,
            commands=[cmd],
            working_directory="/tmp",
            timeout=timeout,
            document_name="AWS-RunShellScript",
        )

        if not command_id:
            raise RuntimeError("Failed to send remote SSM command")

        invocation = None
        for instance_id in self.instance_ids:
            invocation = self.ssm_service.wait_for_command(
                command_id,
                instance_id,
                timeout=timeout,
                poll_interval=5,
            )
            if invocation is None:
                raise RuntimeError(f"SSM command did not complete for instance {instance_id}")

            if invocation.get("status") != "Success":
                return subprocess.CompletedProcess(
                    args=[cmd],
                    returncode=invocation.get("return_code", 1),
                    stdout=invocation.get("output", ""),
                    stderr=invocation.get("error", ""),
                )

        return subprocess.CompletedProcess(
            args=[cmd],
            returncode=invocation.get("return_code", 0),
            stdout=invocation.get("output", ""),
            stderr=invocation.get("error", ""),
        )
