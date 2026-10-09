from __future__ import annotations

from typing import List

from app.bootstrap import AppContext
from app.models.budget import Budget
from app.models.category import Category
from app.services.budget_service import BudgetProgress


class BudgetController:
    """Controller for managing category budgets."""

    def __init__(self, context: AppContext):
        self.context = context

    def get_expense_categories(self) -> List[Category]:
        return self.context.finance_service.list_categories(cat_type="expense", include_archived=False)

    def get_budget_progress(self, year: int, month: int) -> List[BudgetProgress]:
        return self.context.budget_service.get_budget_progress_list(year, month)

    def get_total_summary(self, year: int, month: int) -> dict:
        return self.context.budget_service.get_total_budget_summary(year, month)

    def set_budget(self, category_id: int, amount: int, year: int, month: int) -> Budget:
        return self.context.budget_service.set_budget(
            category_id=category_id,
            amount=amount,
            year=year,
            month=month,
        )

    def delete_budget(self, budget_id: int) -> bool:
        return self.context.budget_service.delete_budget(budget_id)
