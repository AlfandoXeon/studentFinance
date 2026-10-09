from __future__ import annotations

import calendar
import logging
from dataclasses import dataclass
from typing import List, Optional

from app.database.database_manager import DatabaseManager
from app.models.budget import Budget
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.utils.validators import ValidationError, validate_budget_period, validate_positive_amount

logger = logging.getLogger(__name__)


@dataclass
class BudgetProgress:
    """Represents the progress and utilization of a category budget."""

    budget_id: int
    category_id: int
    category_name: str
    budget_amount: int
    used_amount: int
    remaining_amount: int
    percentage: float
    is_warning: bool  # >= threshold (e.g. 80%)
    is_exceeded: bool  # > 100%


class BudgetService:
    """Service for managing category budgets and tracking monthly utilization."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        budget_repo: BudgetRepository,
        category_repo: CategoryRepository,
        warning_threshold: float = 0.80,
    ):
        self.db_manager = db_manager
        self.budget_repo = budget_repo
        self.category_repo = category_repo
        self.warning_threshold = warning_threshold

    def set_budget(self, category_id: int, amount: int, year: int, month: int) -> Budget:
        """Create or update a monthly budget for a category."""
        amount = validate_positive_amount(amount, "budget_amount")
        validate_budget_period(year, month)

        cat = self.category_repo.get_by_id(category_id)
        if not cat:
            raise ValidationError("Kategori tidak ditemukan.")
        if cat.type != "expense":
            raise ValidationError("Anggaran hanya dapat dibuat untuk kategori pengeluaran.")

        existing = self.budget_repo.get_by_category_and_period(category_id, year, month)
        if existing:
            existing.amount = amount
            self.budget_repo.update(existing)
            return existing

        new_budget = Budget(
            category_id=category_id,
            amount=amount,
            period_year=year,
            period_month=month,
        )
        return self.budget_repo.create(new_budget)

    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget by ID."""
        return self.budget_repo.delete(budget_id)

    def get_budget(self, budget_id: int) -> Optional[Budget]:
        """Fetch a budget by ID."""
        return self.budget_repo.get_by_id(budget_id)

    def get_budget_progress_list(self, year: int, month: int) -> List[BudgetProgress]:
        """Calculate utilization for all budgets in a given month.

        Calculates actual qualifying expense transactions within that month.
        """
        validate_budget_period(year, month)
        budgets = self.budget_repo.list_for_period(year, month)
        if not budgets:
            return []

        # Determine start date and end date of month
        _, last_day = calendar.monthrange(year, month)
        start_date = f"{year:04d}-{month:02d}-01"
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"

        # Query total expenses per category in this month
        query = """
            SELECT category_id, COALESCE(SUM(amount), 0) AS total_spent
            FROM transactions
            WHERE type = 'expense'
              AND transaction_date >= ?
              AND transaction_date <= ?
            GROUP BY category_id;
        """

        spent_by_category = {}
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(query, (start_date, end_date))
            for row in cursor.fetchall():
                spent_by_category[row["category_id"]] = int(row["total_spent"])

        results: List[BudgetProgress] = []
        for b in budgets:
            cat = self.category_repo.get_by_id(b.category_id)
            cat_name = cat.name if cat else f"Kategori #{b.category_id}"
            spent = spent_by_category.get(b.category_id, 0)
            remaining = b.amount - spent
            pct = round((spent / b.amount) * 100.0, 2) if b.amount > 0 else 0.0

            results.append(
                BudgetProgress(
                    budget_id=b.id,
                    category_id=b.category_id,
                    category_name=cat_name,
                    budget_amount=b.amount,
                    used_amount=spent,
                    remaining_amount=remaining,
                    percentage=pct,
                    is_warning=(pct >= self.warning_threshold * 100.0 and pct <= 100.0),
                    is_exceeded=(pct > 100.0),
                )
            )
        return results

    def get_total_budget_summary(self, year: int, month: int) -> dict:
        """Get aggregate budget totals for the month."""
        progress_list = self.get_budget_progress_list(year, month)
        total_budget = sum(p.budget_amount for p in progress_list)
        total_used = sum(p.used_amount for p in progress_list)
        total_remaining = total_budget - total_used
        pct = round(total_used / total_budget * 100.0, 2) if total_budget > 0 else 0.0

        return {
            "total_budget": total_budget,
            "total_used": total_used,
            "total_remaining": total_remaining,
            "percentage": pct,
            "items_count": len(progress_list),
            "warnings_count": sum(1 for p in progress_list if p.is_warning or p.is_exceeded),
        }
