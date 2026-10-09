from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.database_manager import DatabaseManager
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.utils.validators import validate_iso_date

logger = logging.getLogger(__name__)


@dataclass
class CategorySpendingItem:
    """Represents spending within a specific category."""

    category_id: int
    category_name: str
    total_amount: int
    percentage: float
    transaction_count: int


@dataclass
class FinancialReport:
    """Comprehensive financial report for a date range."""

    start_date: str
    end_date: str
    total_income: int
    total_expense: int
    net_cashflow: int
    days_count: int
    average_daily_expense: int
    category_spendings: List[CategorySpendingItem]
    top_spending_categories: List[CategorySpendingItem]


class ReportService:
    """Service for financial reports, category aggregations, and data exports."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
        account_repo: AccountRepository,
    ):
        self.db_manager = db_manager
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.account_repo = account_repo

    def generate_report(self, start_date: str, end_date: str) -> FinancialReport:
        """Generate a complete financial report for the given inclusive date range."""
        validate_iso_date(start_date, "start_date")
        validate_iso_date(end_date, "end_date")

        d_start = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
        d_end = datetime.strptime(end_date[:10], "%Y-%m-%d").date()
        if d_end < d_start:
            raise ValueError("Tanggal akhir tidak boleh lebih awal dari tanggal mulai.")

        days_count = max(1, (d_end - d_start).days + 1)

        # 1. Total income and expense (excluding transfers)
        summary_query = """
            SELECT
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
            FROM transactions
            WHERE transaction_date >= ? AND transaction_date <= ?;
        """

        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(summary_query, (start_date, end_date))
            row = cursor.fetchone()
            total_income = int(row["total_income"])
            total_expense = int(row["total_expense"])
            net_cashflow = total_income - total_expense

            # 2. Category spending breakdown
            cat_query = """
                SELECT
                    t.category_id,
                    c.name as category_name,
                    SUM(t.amount) as total_amount,
                    COUNT(t.id) as txn_count
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.type = 'expense'
                  AND t.transaction_date >= ?
                  AND t.transaction_date <= ?
                GROUP BY t.category_id, c.name
                ORDER BY total_amount DESC;
            """
            cat_cursor = conn.execute(cat_query, (start_date, end_date))
            cat_rows = cat_cursor.fetchall()

        category_spendings: List[CategorySpendingItem] = []
        for r in cat_rows:
            amt = int(r["total_amount"])
            pct = round(amt / total_expense * 100.0, 2) if total_expense > 0 else 0.0
            category_spendings.append(
                CategorySpendingItem(
                    category_id=r["category_id"],
                    category_name=r["category_name"],
                    total_amount=amt,
                    percentage=pct,
                    transaction_count=r["txn_count"],
                )
            )

        top_spending = category_spendings[:5]
        avg_daily = total_expense // days_count if days_count > 0 else 0

        return FinancialReport(
            start_date=start_date,
            end_date=end_date,
            total_income=total_income,
            total_expense=total_expense,
            net_cashflow=net_cashflow,
            days_count=days_count,
            average_daily_expense=avg_daily,
            category_spendings=category_spendings,
            top_spending_categories=top_spending,
        )

    def get_daily_trend(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get daily income and expense totals for charting."""
        query = """
            SELECT
                transaction_date,
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS daily_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS daily_expense
            FROM transactions
            WHERE transaction_date >= ? AND transaction_date <= ?
            GROUP BY transaction_date
            ORDER BY transaction_date ASC;
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(query, (start_date, end_date))
            rows = cursor.fetchall()
            return [
                {
                    "date": r["transaction_date"],
                    "income": int(r["daily_income"]),
                    "expense": int(r["daily_expense"]),
                }
                for r in rows
            ]

    def export_transactions_to_csv(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
    ) -> str:
        """Export transactions to CSV string format with human-readable account and category names."""
        txns = self.transaction_repo.list_filtered(
            start_date=start_date,
            end_date=end_date,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
        )

        # Preload accounts and categories mapping
        accounts = {a.id: a.name for a in self.account_repo.list_all(include_archived=True)}
        categories = {c.id: c.name for c in self.category_repo.list_all(include_archived=True)}

        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(
            [
                "ID",
                "Tanggal",
                "Tipe",
                "Nominal",
                "Akun",
                "Akun Tujuan",
                "Kategori",
                "Deskripsi",
            ]
        )

        for t in txns:
            acc_name = accounts.get(t.account_id, str(t.account_id))
            to_acc_name = accounts.get(t.to_account_id, str(t.to_account_id)) if t.to_account_id else ""
            cat_name = categories.get(t.category_id, "") if t.category_id else ""

            writer.writerow(
                [
                    t.id,
                    t.transaction_date,
                    t.type,
                    t.amount,
                    acc_name,
                    to_acc_name,
                    cat_name,
                    t.description or "",
                ]
            )

        return output.getvalue()
