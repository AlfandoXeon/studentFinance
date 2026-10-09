from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.utils.validators import validate_account_type, validate_opening_balance


@dataclass
class Account:
    """Domain model representing a financial account (e.g. Cash, Bank, E-Wallet)."""

    name: str
    account_type: str  # 'cash', 'bank', 'e_wallet'
    opening_balance: int = 0
    id: Optional[int] = None
    created_at: str = ""
    is_archived: bool = False

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nama akun tidak boleh kosong.")
        self.name = self.name.strip()
        self.account_type = validate_account_type(self.account_type)
        self.opening_balance = validate_opening_balance(self.opening_balance)
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
