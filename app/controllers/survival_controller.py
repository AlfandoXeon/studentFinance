from __future__ import annotations

from typing import Optional

from app.bootstrap import AppContext
from app.services.survival_mode_service import SurvivalEstimate


class SurvivalController:
    """Controller for Student Survival Mode calculations."""

    def __init__(self, context: AppContext):
        self.context = context

    def get_current_balance(self) -> int:
        return self.context.finance_service.get_total_balance()

    def calculate_survival(
        self,
        expected_income_date: str,
        planned_mandatory_expenses: int = 0,
        custom_balance: Optional[int] = None,
    ) -> SurvivalEstimate:
        return self.context.survival_service.calculate_estimate(
            expected_income_date=expected_income_date,
            planned_mandatory_expenses=planned_mandatory_expenses,
            custom_balance=custom_balance,
        )
