from __future__ import annotations

from PySide6.QtCore import Qt

from app.bootstrap import AppContext
from app.views.main_window import MainWindow


def test_main_window_startup_and_navigation(app_context: AppContext, qtbot):
    """Test that MainWindow launches, all pages switch without error, and views refresh."""
    window = MainWindow(app_context)
    qtbot.addWidget(window)
    window.show()

    assert window.isVisible()
    assert window.windowTitle() == "Student Finance"

    # Verify 8 navigation buttons exist with proper text
    assert len(window.nav_buttons) == 8
    assert window.nav_buttons[2].text() == "Akun && Dompet"
    assert window.nav_buttons[7].text() == "Pengaturan && Backup"

    # Verify action column widths are wide enough to prevent clipping
    assert window.accounts_view.table.columnWidth(5) >= 200
    assert window.transactions_view.table.columnWidth(6) >= 140

    # Test switching to every single page
    for i in range(8):
        window.switch_page(i)
        assert window.stack.currentIndex() == i
        # Verify page title updated
        assert window.header_page_title.text() != ""

    # Switch back to Transactions page (index 1)
    window.switch_page(1)
    assert window.transactions_view.table is not None


def test_transaction_creation_and_ui_sync(app_context: AppContext, qtbot):
    """Test that transactions can be created and the UI stays in sync."""
    window = MainWindow(app_context)
    qtbot.addWidget(window)
    window.show()

    # Pre-seed an account
    acc = app_context.finance_service.create_account("Dompet Tunai", "cash", 100_000)
    cat = app_context.finance_service.list_categories("expense")[0]

    # Create transaction via controller
    app_context.finance_service.create_expense(
        amount=25_000,
        account_id=acc.id,
        category_id=cat.id,
        transaction_date="2026-10-09",
        description="Beli Nasi Goreng",
    )

    # Trigger global data changed refresh
    window.on_global_data_changed()

    # Switch to transactions view and check row count
    window.switch_page(1)
    assert window.transactions_view.table.rowCount() >= 1

    # Switch to dashboard and verify balance reflected
    window.switch_page(0)
    assert "75.000" in window.dashboard_view.card_total_balance.value_label.text()


def test_dialogs_enter_key_and_currency_formatting(app_context: AppContext, qtbot):
    """Test that all dialogs configure save button as default (Enter key) and use CurrencyLineEdit."""
    from app.views.dialogs.account_dialog import AccountDialog
    from app.views.dialogs.budget_dialog import BudgetDialog
    from app.views.dialogs.category_dialog import CategoryDialog
    from app.views.dialogs.transaction_dialog import TransactionDialog

    accounts = app_context.finance_service.list_accounts()
    categories = app_context.finance_service.list_categories()

    # TransactionDialog
    txn_dlg = TransactionDialog(accounts=accounts, categories=categories)
    qtbot.addWidget(txn_dlg)
    assert txn_dlg.save_btn.isDefault() is True
    # Test live typing 100000 becomes 100,000
    txn_dlg.amount_input._format_live("100000")
    assert txn_dlg.amount_input.text() == "100,000"

    # AccountDialog
    acc_dlg = AccountDialog()
    qtbot.addWidget(acc_dlg)
    assert acc_dlg.save_btn.isDefault() is True
    acc_dlg.balance_input._format_live("1500000")
    assert acc_dlg.balance_input.text() == "1,500,000"

    # CategoryDialog
    cat_dlg = CategoryDialog()
    qtbot.addWidget(cat_dlg)
    assert cat_dlg.save_btn.isDefault() is True

    # BudgetDialog
    bgt_dlg = BudgetDialog(categories=categories)
    qtbot.addWidget(bgt_dlg)
    assert bgt_dlg.save_btn.isDefault() is True
    bgt_dlg.amount_input._format_live("200000")
    assert bgt_dlg.amount_input.text() == "200,000"


def test_settings_view_user_name_update(app_context: AppContext, qtbot):
    """Test user profile name update in settings view and header sync."""
    window = MainWindow(app_context)
    qtbot.addWidget(window)
    window.show()

    # Switch to Settings page (index 7)
    window.switch_page(7)
    settings_view = window.settings_view

    # Initially user name in DB is empty
    assert app_context.user_profile_repo.get_user_name() is None

    # Enter new name and save
    settings_view.name_input.setText("Alfando")
    qtbot.mouseClick(settings_view.btn_save_name, Qt.LeftButton)

    # Verify persisted in database
    assert app_context.user_profile_repo.get_user_name() == "Alfando"
    # Verify header greeting updated
    assert "Alfando" in window.user_greeting_lbl.text()
    # Verify dashboard title updated
    assert "Alfando" in window.dashboard_view.page_title.text()
