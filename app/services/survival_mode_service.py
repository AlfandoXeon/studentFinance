from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.repositories.transaction_repository import TransactionRepository
from app.utils.validators import ValidationError, validate_iso_date

logger = logging.getLogger(__name__)


@dataclass
class SurvivalEstimate:
    """Represents the student survival calculation output."""

    current_balance: int
    planned_mandatory_expenses: int
    available_discretionary: int
    target_date: str
    days_remaining: int
    daily_allowance: int
    is_deficit: bool
    deficit_amount: int
    status_message: str


class SurvivalModeService:
    """Service to calculate safe daily spending limit until next income."""

    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def calculate_estimate(
        self,
        expected_income_date: str,
        planned_mandatory_expenses: int = 0,
        custom_balance: Optional[int] = None,
        as_of_date: Optional[str] = None,
    ) -> SurvivalEstimate:
        """Calculate daily spending limit.

        Day-counting convention:
        Survives from `as_of_date` (inclusive) up to `expected_income_date` (exclusive).
        For example: today 09 Oct, next income 14 Oct -> 5 days remaining (9, 10, 11, 12, 13).
        If expected_income_date is today or in the past, days_remaining is clamped to 1 with an alert.
        """
        validate_iso_date(expected_income_date, "expected_income_date")
        if planned_mandatory_expenses < 0:
            raise ValidationError("Rencana pengeluaran wajib tidak boleh negatif.")

        target_dt = datetime.strptime(expected_income_date[:10], "%Y-%m-%d").date()

        if as_of_date:
            validate_iso_date(as_of_date, "as_of_date")
            current_dt = datetime.strptime(as_of_date[:10], "%Y-%m-%d").date()
        else:
            current_dt = date.today()

        days_diff = (target_dt - current_dt).days

        # Available balance
        if custom_balance is not None:
            available_balance = custom_balance
        else:
            available_balance = self.transaction_repo.get_total_balance_across_active_accounts()

        discretionary = available_balance - planned_mandatory_expenses

        if days_diff <= 0:
            days_remaining = 1
            if days_diff == 0:
                note = "Hari pemasukan dijadwalkan hari ini."
            else:
                note = "Tanggal pemasukan telah lewat dari tanggal evaluasi."
        else:
            days_remaining = days_diff
            note = f"Tersisa {days_remaining} hari hingga pemasukan berikutnya."

        if discretionary < 0:
            is_deficit = True
            deficit_amount = abs(discretionary)
            daily_allowance = 0
            status_message = (
                f"Peringatan defisit! Saldo tidak mencukupi untuk kebutuhan wajib "
                f"(kurang Rp {deficit_amount:,}). Tidak ada sisa untuk belanja harian.".replace(",", ".")
            )
        else:
            is_deficit = False
            deficit_amount = 0
            daily_allowance = discretionary // days_remaining
            status_message = (f"{note} Estimasi batas belanja aman per hari adalah Rp {daily_allowance:,}.").replace(
                ",", "."
            )

        return SurvivalEstimate(
            current_balance=available_balance,
            planned_mandatory_expenses=planned_mandatory_expenses,
            available_discretionary=discretionary,
            target_date=expected_income_date[:10],
            days_remaining=days_remaining,
            daily_allowance=daily_allowance,
            is_deficit=is_deficit,
            deficit_amount=deficit_amount,
            status_message=status_message,
        )
