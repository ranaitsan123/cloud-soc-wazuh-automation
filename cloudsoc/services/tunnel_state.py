from __future__ import annotations

from pathlib import Path
from typing import Optional

from cloudsoc.models.tunnel import TunnelSessionData


class TunnelStateStore:
    def __init__(self, state_dir: Optional[Path] = None) -> None:
        self.state_dir = state_dir or Path.home() / ".cloud-soc"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self.state_dir / "dashboard_tunnel.json"

    def load(self) -> Optional[TunnelSessionData]:
        if not self.path.exists():
            return None

        try:
            return TunnelSessionData.model_validate_json(self.path.read_text())
        except Exception:
            self.remove()
            return None

    def save(self, session_data: TunnelSessionData) -> None:
        self.path.write_text(session_data.model_dump_json())

    def remove(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
