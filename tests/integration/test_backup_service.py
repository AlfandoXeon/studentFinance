from __future__ import annotations

from pathlib import Path

from app.bootstrap import AppContext


def test_backup_and_restore_service(app_context: AppContext, tmp_path: Path):
    fin = app_context.finance_service
    backup_svc = app_context.backup_service

    # Create an account and transaction
    acc = fin.create_account("Tabungan", "bank", 1_000_000)
    cat = fin.list_categories("expense")[0]
    fin.create_expense(200_000, acc.id, cat.id, "2026-10-09", "Buku Kuliah")

    assert fin.get_account_balance(acc.id) == 800_000

    # 1. Create backup
    backup_path = backup_svc.create_backup("test_backup.db")
    assert backup_path.exists()
    assert backup_svc.validate_backup_file(backup_path) is True

    # 2. Mutate live database by adding another expense
    fin.create_expense(300_000, acc.id, cat.id, "2026-10-09", "Makan Malam")
    assert fin.get_account_balance(acc.id) == 500_000

    # 3. Restore backup
    recovery_snapshot = backup_svc.restore_backup(backup_path)
    assert recovery_snapshot.exists()

    # Verify live balance is restored to 800.000!
    assert fin.get_account_balance(acc.id) == 800_000
