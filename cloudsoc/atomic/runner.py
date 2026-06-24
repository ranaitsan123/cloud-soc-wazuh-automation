import subprocess
from pathlib import Path
from typing import Dict, Any

import yaml

SCENARIOS_FILE = Path("/opt/fortress/atomics/scenarios.yml")


class AtomicRunner:

    def __init__(self, scenarios_file: Path = SCENARIOS_FILE) -> None:
        self.scenarios_file = Path(scenarios_file)

    def list(self) -> Dict[str, Any]:
        if not self.scenarios_file.exists():
            raise FileNotFoundError(f"Scenarios file not found: {self.scenarios_file}")

        data = yaml.safe_load(self.scenarios_file.read_text()) or {}
        return data.get("scenarios", {})

    def run(self, technique_id: str) -> subprocess.CompletedProcess[str]:
        scenarios = self.list()
        if technique_id not in scenarios:
            raise ValueError(f"Unknown technique: {technique_id}")

        cmd = scenarios[technique_id].get("command")
        if not cmd:
            raise ValueError(f"No command defined for technique: {technique_id}")

        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True,
        )

        return result
