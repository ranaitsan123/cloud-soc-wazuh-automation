from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from cloudsoc.models.deployment import DeploymentState, DeploymentTargetState


class DeploymentStateStore:
    def __init__(self, state_dir: Optional[Path] = None) -> None:
        self.state_dir = state_dir or Path.home() / ".cloud-soc"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self.state_dir / "deployment_state.json"

    def load(self) -> Optional[DeploymentState]:
        if not self.path.exists():
            return None

        try:
            return DeploymentState.model_validate_json(self.path.read_text())
        except Exception:
            return None

    def save(self, state: DeploymentState) -> None:
        self.path.write_text(state.model_dump_json(indent=2))

    def initialize(self, deployment_names: List[str]) -> DeploymentState:
        now = time.time()
        targets = {
            name: DeploymentTargetState()
            for name in deployment_names
        }
        state = DeploymentState(
            started_at=now,
            status="in_progress",
            targets=targets,
        )
        self.save(state)
        return state
