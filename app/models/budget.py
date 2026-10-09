from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.utils.validators import validate_budget_period, validate_positive_amount


@dataclass
class Budget:
    """Domain model representing a monthly budget for an expense category."""

    category_id: int
    amount: int
    period_year: int
    period_month: int
    id: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        self.amount = validate_positive_amount(self.amount, "budget_amount")
        validate_budget_period(self.period_year, self.period_month)

        now_iso = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now_iso
        if not self.updated_at:
            self.updated_at = now_iso
