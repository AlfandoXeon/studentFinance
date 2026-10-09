from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.utils.validators import (
    validate_iso_date,
    validate_positive_amount,
    validate_transaction_type,
    validate_transfer_accounts,
)


@dataclass
class Transaction:
    """Domain model representing a financial transaction."""

    type: str  # 'income', 'expense', 'transfer'
    amount: int
    account_id: int
    transaction_date: str  # YYYY-MM-DD
    id: Optional[int] = None
    to_account_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.type = validate_transaction_type(self.type)
        self.amount = validate_positive_amount(self.amount)
        self.transaction_date = validate_iso_date(self.transaction_date, "transaction_date")

        if self.type == "transfer":
            validate_transfer_accounts(self.account_id, self.to_account_id)
            if self.category_id is not None:
                # Transfers do not belong to income or expense categories
                self.category_id = None
        else:
            if self.to_account_id is not None:
                raise ValueError("Transaksi income dan expense tidak boleh memiliki to_account_id.")

        now_iso = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now_iso
        if not self.updated_at:
            self.updated_at = now_iso
