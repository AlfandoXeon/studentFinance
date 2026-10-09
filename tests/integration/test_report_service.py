from __future__ import annotations

from app.bootstrap import AppContext


def test_report_service(app_context: AppContext):
    fin = app_context.finance_service
    rep = app_context.report_service

    acc = fin.create_account("Rekening Utama", "bank", 2_000_000)
    inc_cat = fin.list_categories("income")[0]
    exp_cats = fin.list_categories("expense")
    cat_food = exp_cats[0]
    cat_transport = exp_cats[1]

    # Create transactions
    fin.create_income(1_000_000, acc.id, inc_cat.id, "2026-10-01", "Gaji Part-time")
    fin.create_expense(100_000, acc.id, cat_food.id, "2026-10-02", "Makan resto")
    fin.create_expense(50_000, acc.id, cat_transport.id, "2026-10-03", "Bensin")

    report = rep.generate_report("2026-10-01", "2026-10-10")
    assert report.total_income == 1_000_000
    assert report.total_expense == 150_000
    assert report.net_cashflow == 850_000
    assert report.days_count == 10
    assert report.average_daily_expense == 15_000  # 150.000 // 10 days
    assert len(report.category_spendings) == 2
    assert report.category_spendings[0].category_name == cat_food.name
    assert report.category_spendings[0].total_amount == 100_000

    # CSV Export
    csv_data = rep.export_transactions_to_csv("2026-10-01", "2026-10-10")
    assert "Gaji Part-time" in csv_data
    assert "Makan resto" in csv_data
    assert "100000" in csv_data
