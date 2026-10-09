from __future__ import annotations

from datetime import datetime
from typing import Optional


class ValidationError(ValueError):
    """Raised when data fails domain validation rules."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field


def validate_positive_amount(amount: int, field_name: str = "amount") -> int:
    """Validate that amount is an integer strictly greater than zero."""
    if not isinstance(amount, int):
        raise ValidationError(f"Nominal harus berupa integer, didapatkan {type(amount).__name__}", field=field_name)
    if amount <= 0:
        raise ValidationError("Nominal harus lebih besar dari 0 Rupiah.", field=field_name)
    if amount > 100_000_000_000:  # Reasonable sanity check (100 Billion IDR)
        raise ValidationError("Nominal melebihi batas wajar maksimum.", field=field_name)
    return amount


def validate_opening_balance(amount: int, field_name: str = "opening_balance") -> int:
    """Validate opening balance, which can be 0 or positive integer."""
    if not isinstance(amount, int):
        raise ValidationError(f"Saldo awal harus berupa integer, didapatkan {type(amount).__name__}", field=field_name)
    if amount < 0:
        raise ValidationError("Saldo awal tidak boleh negatif.", field=field_name)
    return amount


def validate_transaction_type(t_type: str) -> str:
    """Validate transaction type: income, expense, transfer."""
    allowed = {"income", "expense", "transfer"}
    if t_type not in allowed:
        raise ValidationError(
            f"Tipe transaksi tidak valid: '{t_type}'. Harus salah satu dari {allowed}",
            field="type",
        )
    return t_type


def validate_account_type(a_type: str) -> str:
    """Validate account type: cash, bank, e_wallet."""
    allowed = {"cash", "bank", "e_wallet"}
    if a_type not in allowed:
        raise ValidationError(
            f"Tipe akun tidak valid: '{a_type}'. Harus salah satu dari {allowed}",
            field="account_type",
        )
    return a_type


def validate_category_type(c_type: str) -> str:
    """Validate category type: income, expense."""
    allowed = {"income", "expense"}
    if c_type not in allowed:
        raise ValidationError(
            f"Tipe kategori tidak valid: '{c_type}'. Harus 'income' atau 'expense'",
            field="type",
        )
    return c_type


def validate_iso_date(date_str: str, field_name: str = "date") -> str:
    """Validate that the string is a valid ISO date YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS."""
    if not isinstance(date_str, str):
        raise ValidationError("Tanggal harus berupa string format ISO.", field=field_name)
    clean_date = date_str[:10]
    try:
        datetime.strptime(clean_date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            f"Format tanggal tidak valid: '{date_str}'. Gunakan format YYYY-MM-DD.",
            field=field_name,
        )
    return date_str


def validate_budget_period(year: int, month: int) -> None:
    """Validate year and month for budget period."""
    if not isinstance(year, int) or year < 2000 or year > 2100:
        raise ValidationError("Tahun anggaran tidak valid (2000-2100).", field="period_year")
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValidationError("Bulan anggaran tidak valid (1-12).", field="period_month")


def validate_transfer_accounts(source_id: int, dest_id: Optional[int]) -> None:
    """Validate that transfer has a valid and distinct destination account."""
    if dest_id is None:
        raise ValidationError("Akun tujuan transfer wajib diisi.", field="to_account_id")
    if source_id == dest_id:
        raise ValidationError("Akun sumber dan akun tujuan transfer tidak boleh sama.", field="to_account_id")
