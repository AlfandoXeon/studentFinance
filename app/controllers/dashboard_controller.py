from __future__ import annotations

import calendar
from datetime import date
from typing import Any, Dict

from app.bootstrap import AppContext


class DashboardController:
    """Controller for the main overview dashboard."""

    def __init__(self, context: AppContext):
        self.context = context

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Gather all metrics, recent transactions, budget and survival summaries for the dashboard."""
        today = date.today()
        year = today.year
        month = today.month

        # 1. Total balance
        total_balance = self.context.finance_service.get_total_balance()

        # 2. Today's income & expense
        today_income, today_expense = self.context.finance_service.get_today_cashflow()

        # 3. Monthly cashflow
        _, last_day = calendar.monthrange(year, month)
        start_month = f"{year:04d}-{month:02d}-01"
        end_month = f"{year:04d}-{month:02d}-{last_day:02d}"
        month_inc, month_exp, month_net = self.context.finance_service.get_cashflow_summary(start_month, end_month)

        # 4. Budget summary
        budget_summary = self.context.budget_service.get_total_budget_summary(year, month)

        # 5. Recent 5 transactions
        recent_txns = self.context.finance_service.list_transactions(limit=5)

        # Preload mappings for display
        accounts = {a.id: a.name for a in self.context.account_repo.list_all(include_archived=True)}
        categories = {c.id: c.name for c in self.context.category_repo.list_all(include_archived=True)}

        formatted_txns = []
        for t in recent_txns:
            acc_name = accounts.get(t.account_id, "Akun")
            to_acc_name = accounts.get(t.to_account_id, "") if t.to_account_id else ""
            cat_name = categories.get(t.category_id, "-") if t.category_id else "-"
            formatted_txns.append(
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": t.amount,
                    "account_name": acc_name,
                    "to_account_name": to_acc_name,
                    "category_name": cat_name,
                    "date": t.transaction_date,
                    "description": t.description or "",
                }
            )

        # 6. Survival snapshot (default evaluate until 25th of current or next month, or 7 days ahead)
        survival_target = today.replace(day=25) if today.day < 25 else today.replace(month=month % 12 + 1, day=1)
        survival_info = self.context.survival_service.calculate_estimate(
            expected_income_date=survival_target.isoformat(),
            planned_mandatory_expenses=0,
            custom_balance=total_balance,
        )

        return {
            "total_balance": total_balance,
            "today_income": today_income,
            "today_expense": today_expense,
            "month_income": month_inc,
            "month_expense": month_exp,
            "month_net": month_net,
            "budget_summary": budget_summary,
            "recent_transactions": formatted_txns,
            "survival_info": survival_info,
        }
