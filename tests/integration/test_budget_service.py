from __future__ import annotations

from app.bootstrap import AppContext


def test_budget_service(app_context: AppContext):
    fin = app_context.finance_service
    budget_svc = app_context.budget_service

    acc = fin.create_account("Dompet", "cash", 500_000)
    exp_cat = fin.list_categories("expense")[0]

    # Set budget for category: 200.000 for October 2026
    budget = budget_svc.set_budget(
        category_id=exp_cat.id,
        amount=200_000,
        year=2026,
        month=10,
    )
    assert budget.id is not None
    assert budget.amount == 200_000

    # Initial progress: used 0
    progress = budget_svc.get_budget_progress_list(2026, 10)
    assert len(progress) == 1
    assert progress[0].used_amount == 0
    assert progress[0].remaining_amount == 200_000
    assert progress[0].percentage == 0.0
    assert not progress[0].is_warning
    assert not progress[0].is_exceeded

    # Add expense of 170.000 (85% utilization -> warning triggered)
    fin.create_expense(
        amount=170_000,
        account_id=acc.id,
        category_id=exp_cat.id,
        transaction_date="2026-10-09",
    )

    progress = budget_svc.get_budget_progress_list(2026, 10)
    assert progress[0].used_amount == 170_000
    assert progress[0].remaining_amount == 30_000
    assert progress[0].percentage == 85.0
    assert progress[0].is_warning is True
    assert progress[0].is_exceeded is False

    # Add another expense of 50.000 (Total 220.000 -> 110% exceeded)
    fin.create_expense(
        amount=50_000,
        account_id=acc.id,
        category_id=exp_cat.id,
        transaction_date="2026-10-10",
    )

    progress = budget_svc.get_budget_progress_list(2026, 10)
    assert progress[0].used_amount == 220_000
    assert progress[0].remaining_amount == -20_000
    assert progress[0].percentage == 110.0
    assert progress[0].is_exceeded is True
