from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TunnelSessionData(BaseModel):
    instance_id: str
    session_id: str
    local_port: int
    remote_port: int
    started_at: float
    local_address: str = "127.0.0.1"
    pid: Optional[int] = None
