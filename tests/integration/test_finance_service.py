from __future__ import annotations

import pytest

from app.bootstrap import AppContext
from app.utils.validators import ValidationError


def test_finance_service_operations(app_context: AppContext):
    service = app_context.finance_service

    # 1. Accounts
    bank = service.create_account("Bank BCA", "bank", opening_balance=1_000_000)
    assert bank.id is not None
    assert service.get_account_balance(bank.id) == 1_000_000

    wallet = service.create_account("Dompet Kuliah", "cash", opening_balance=100_000)
    assert wallet.id is not None
    assert service.get_account_balance(wallet.id) == 100_000

    # 2. Categories
    inc_cats = service.list_categories(cat_type="income")
    exp_cats = service.list_categories(cat_type="expense")
    assert len(inc_cats) > 0
    assert len(exp_cats) > 0

    income_cat = inc_cats[0]
    expense_cat = exp_cats[0]

    # 3. Income Transaction
    service.create_income(
        amount=500_000,
        account_id=bank.id,
        category_id=income_cat.id,
        transaction_date="2026-10-09",
        description="Kiriman bulanan",
    )
    assert service.get_account_balance(bank.id) == 1_500_000

    # 4. Expense Transaction
    service.create_expense(
        amount=40_000,
        account_id=wallet.id,
        category_id=expense_cat.id,
        transaction_date="2026-10-09",
        description="Makan siang",
    )
    assert service.get_account_balance(wallet.id) == 60_000

    # 5. Transfer Transaction
    service.create_transfer(
        amount=200_000,
        source_account_id=bank.id,
        dest_account_id=wallet.id,
        transaction_date="2026-10-09",
        description="Tarik tunai ATM",
    )
    assert service.get_account_balance(bank.id) == 1_300_000
    assert service.get_account_balance(wallet.id) == 260_000

    # 6. Consolidated Cashflow (Transfers strictly excluded)
    inc, exp, net = service.get_cashflow_summary("2026-10-01", "2026-10-31")
    assert inc == 500_000
    assert exp == 40_000
    assert net == 460_000

    # 7. Total balance
    # Total active balance = 1.300.000 + 260.000 + seeded default account (0) = 1.560.000
    assert service.get_total_balance() == 1_560_000

    # 8. Deletion restriction
    with pytest.raises(ValueError):
        service.delete_account(bank.id)


def test_invalid_category_type_rejection(app_context: AppContext):
    service = app_context.finance_service
    acc = service.create_account("Test Bank", "bank", 100_000)
    inc_cat = service.list_categories("income")[0]
    exp_cat = service.list_categories("expense")[0]

    # Try creating expense with income category
    with pytest.raises(ValidationError):
        service.create_expense(50_000, acc.id, inc_cat.id, "2026-10-09")

    # Try creating income with expense category
    with pytest.raises(ValidationError):
        service.create_income(50_000, acc.id, exp_cat.id, "2026-10-09")
