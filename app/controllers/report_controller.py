from __future__ import annotations

from app.bootstrap import AppContext
from app.services.report_service import FinancialReport


class ReportController:
    """Controller for generating financial reports and exports."""

    def __init__(self, context: AppContext):
        self.context = context

    def generate_report(self, start_date: str, end_date: str) -> FinancialReport:
        return self.context.report_service.generate_report(start_date, end_date)

    def export_csv(self, start_date: str, end_date: str) -> str:
        return self.context.report_service.export_transactions_to_csv(start_date=start_date, end_date=end_date)
