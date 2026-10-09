from __future__ import annotations

from app.bootstrap import AppContext


def test_survival_mode_service(app_context: AppContext):
    fin = app_context.finance_service
    surv = app_context.survival_service

    # Create account with 500.000 balance
    fin.create_account("Uang Bulanan", "bank", 500_000)

    # Today: 2026-10-09, Expected income: 2026-10-14 -> 5 days
    # Planned mandatory: 100.000 (e.g. bayar WiFi)
    # Discretionary: 500.000 - 100.000 = 400.000
    # Daily allowance: 400.000 // 5 = 80.000
    est = surv.calculate_estimate(
        expected_income_date="2026-10-14",
        planned_mandatory_expenses=100_000,
        as_of_date="2026-10-09",
    )
    assert est.days_remaining == 5
    assert est.available_discretionary == 400_000
    assert est.daily_allowance == 80_000
    assert est.is_deficit is False

    # Deficit case:
    # Planned mandatory: 600.000, balance 500.000 -> deficit 100.000
    est_def = surv.calculate_estimate(
        expected_income_date="2026-10-14",
        planned_mandatory_expenses=600_000,
        as_of_date="2026-10-09",
    )
    assert est_def.is_deficit is True
    assert est_def.deficit_amount == 100_000
    assert est_def.daily_allowance == 0
