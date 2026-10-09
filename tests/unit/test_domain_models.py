from __future__ import annotations

import pytest

from app.models.account import Account
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction


def test_account_model():
    acc = Account(name="BCA", account_type="bank", opening_balance=500000)
    assert acc.name == "BCA"
    assert acc.account_type == "bank"
    assert acc.opening_balance == 500000
    assert acc.is_archived is False
    assert acc.created_at != ""

    with pytest.raises(ValueError):
        Account(name="", account_type="bank")


def test_category_model():
    cat = Category(name="Makan", type="expense")
    assert cat.name == "Makan"
    assert cat.type == "expense"
    assert cat.is_archived is False

    with pytest.raises(ValueError):
        Category(name="", type="expense")


def test_transaction_model():
    # Valid expense
    txn = Transaction(type="expense", amount=25000, account_id=1, category_id=2, transaction_date="2026-10-09")
    assert txn.amount == 25000
    assert txn.to_account_id is None

    # Invalid expense with to_account_id
    with pytest.raises(ValueError):
        Transaction(
            type="expense",
            amount=25000,
            account_id=1,
            to_account_id=2,
            transaction_date="2026-10-09",
        )

    # Valid transfer
    transfer_txn = Transaction(
        type="transfer",
        amount=100000,
        account_id=1,
        to_account_id=2,
        category_id=5,
        transaction_date="2026-10-09",
    )
    assert transfer_txn.category_id is None  # Transfers automatically clear category_id


def test_budget_model():
    b = Budget(category_id=1, amount=1000000, period_year=2026, period_month=10)
    assert b.amount == 1000000
    assert b.period_year == 2026
    assert b.period_month == 10
