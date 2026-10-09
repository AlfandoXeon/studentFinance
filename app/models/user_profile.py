from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserProfile:
    """Domain model representing user profile settings."""

    name: Optional[str] = None
    id: int = 1
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                self.name = None
