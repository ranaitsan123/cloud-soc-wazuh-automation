from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel, Field


class DeploymentTargetState(BaseModel):
    status: str = "pending"
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    current_task: Optional[str] = None
    error: str = ""
    error_detail: str = ""


class DeploymentState(BaseModel):
    started_at: float
    finished_at: Optional[float] = None
    status: str = "in_progress"
    targets: Dict[str, DeploymentTargetState] = Field(default_factory=dict)
