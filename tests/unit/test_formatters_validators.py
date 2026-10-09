from __future__ import annotations

import pytest

from app.utils.formatters import format_currency, format_date_display, parse_currency
from app.utils.validators import (
    ValidationError,
    validate_account_type,
    validate_budget_period,
    validate_category_type,
    validate_iso_date,
    validate_opening_balance,
    validate_positive_amount,
    validate_transaction_type,
    validate_transfer_accounts,
)


def test_format_currency():
    assert format_currency(0) == "Rp 0"
    assert format_currency(50000) == "Rp 50.000"
    assert format_currency(1500000) == "Rp 1.500.000"
    assert format_currency(-75000) == "-Rp 75.000"

    with pytest.raises(TypeError):
        format_currency(1500.50)  # type: ignore


def test_parse_currency():
    assert parse_currency("1500000") == 1500000
    assert parse_currency("Rp 1.500.000") == 1500000
    assert parse_currency("  Rp 50.000  ") == 50000
    assert parse_currency("25,000") == 25000

    with pytest.raises(ValueError):
        parse_currency("0")
    with pytest.raises(ValueError):
        parse_currency("-50000")
    with pytest.raises(ValueError):
        parse_currency("abc")


def test_format_date_display():
    assert format_date_display("2026-10-09") == "09 Oktober 2026"
    assert format_date_display("2026-10-09", short=True) == "09 Okt 2026"


def test_validators():
    assert validate_positive_amount(1000) == 1000
    with pytest.raises(ValidationError):
        validate_positive_amount(0)
    with pytest.raises(ValidationError):
        validate_positive_amount(-100)

    assert validate_opening_balance(0) == 0
    assert validate_opening_balance(50000) == 50000
    with pytest.raises(ValidationError):
        validate_opening_balance(-1)

    assert validate_transaction_type("income") == "income"
    assert validate_transaction_type("expense") == "expense"
    assert validate_transaction_type("transfer") == "transfer"
    with pytest.raises(ValidationError):
        validate_transaction_type("invalid")

    assert validate_account_type("cash") == "cash"
    assert validate_account_type("bank") == "bank"
    assert validate_account_type("e_wallet") == "e_wallet"
    with pytest.raises(ValidationError):
        validate_account_type("crypto")

    assert validate_category_type("income") == "income"
    assert validate_category_type("expense") == "expense"
    with pytest.raises(ValidationError):
        validate_category_type("other")

    assert validate_iso_date("2026-10-09") == "2026-10-09"
    with pytest.raises(ValidationError):
        validate_iso_date("09-10-2026")

    validate_budget_period(2026, 10)
    with pytest.raises(ValidationError):
        validate_budget_period(1999, 5)
    with pytest.raises(ValidationError):
        validate_budget_period(2026, 13)

    validate_transfer_accounts(1, 2)
    with pytest.raises(ValidationError):
        validate_transfer_accounts(1, 1)
    with pytest.raises(ValidationError):
        validate_transfer_accounts(1, None)
