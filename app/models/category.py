from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.utils.validators import validate_category_type


@dataclass
class Category:
    """Domain model representing an income or expense category."""

    name: str
    type: str  # 'income' or 'expense'
    id: Optional[int] = None
    is_archived: bool = False
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nama kategori tidak boleh kosong.")
        self.name = self.name.strip()
        self.type = validate_category_type(self.type)
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
