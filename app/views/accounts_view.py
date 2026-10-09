from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.controllers.account_controller import AccountController
from app.models.account import Account
from app.utils.formatters import format_currency
from app.views.dialogs.account_dialog import AccountDialog


class AccountsView(QWidget):
    """View for managing financial accounts (Cash, Bank, E-Wallet)."""

    def __init__(
        self,
        controller: AccountController,
        on_data_changed: Optional[Callable] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.on_data_changed = on_data_changed
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Daftar Akun & Dompet")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Kelola rekening bank, uang tunai, dan saldo e-wallet.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.show_archived_cb = QCheckBox("Tampilkan akun arsip")
        self.show_archived_cb.stateChanged.connect(self.refresh_data)
        header_layout.addWidget(self.show_archived_cb)

        self.add_btn = QPushButton("+ Tambah Akun Baru")
        self.add_btn.setProperty("class", "primary-btn")
        self.add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self.add_btn)

        main_layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Nama Akun",
                "Tipe",
                "Saldo Awal",
                "Saldo Saat Ini",
                "Status",
                "Aksi",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 235)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table)

    def refresh_data(self) -> None:
        """Fetch accounts with calculated balances and refresh table."""
        include_archived = self.show_archived_cb.isChecked()
        account_items = self.controller.list_accounts_with_balances(include_archived=include_archived)

        self.table.setRowCount(len(account_items))
        for row_idx, item in enumerate(account_items):
            acc: Account = item["account"]
            bal: int = item["current_balance"]

            # Name
            self.table.setItem(row_idx, 0, QTableWidgetItem(acc.name))

            # Type
            type_label = "Tunai"
            if acc.account_type == "bank":
                type_label = "Rekening Bank"
            elif acc.account_type == "e_wallet":
                type_label = "E-Wallet"
            item_type = QTableWidgetItem(type_label)
            item_type.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_type)

            # Opening balance
            item_open = QTableWidgetItem(format_currency(acc.opening_balance))
            item_open.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, item_open)

            # Current balance
            item_bal = QTableWidgetItem(format_currency(bal))
            item_bal.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_bal.setForeground(Qt.GlobalColor.green if bal >= 0 else Qt.GlobalColor.red)
            self.table.setItem(row_idx, 3, item_bal)

            # Status
            status_text = "Arsip" if acc.is_archived else "Aktif"
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 4, item_status)

            # Actions
            action_widget = QWidget()
            btn_box = QHBoxLayout(action_widget)
            btn_box.setContentsMargins(4, 2, 4, 2)
            btn_box.setSpacing(6)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(55)
            edit_btn.clicked.connect(lambda checked=False, a=acc: self._open_edit_dialog(a))
            btn_box.addWidget(edit_btn)

            archive_btn = QPushButton("Aktifkan" if acc.is_archived else "Arsipkan")
            archive_btn.setFixedWidth(80)
            archive_btn.clicked.connect(
                lambda checked=False, a_id=acc.id, is_arch=acc.is_archived: self._toggle_archive(a_id, is_arch)
            )
            btn_box.addWidget(archive_btn)

            del_btn = QPushButton("Hapus")
            del_btn.setFixedWidth(65)
            del_btn.setProperty("class", "danger-btn")
            del_btn.clicked.connect(lambda checked=False, a_id=acc.id: self._confirm_delete(a_id))
            btn_box.addWidget(del_btn)

            self.table.setCellWidget(row_idx, 5, action_widget)

    def _open_add_dialog(self) -> None:
        dialog = AccountDialog(parent=self)
        if dialog.exec():
            try:
                self.controller.create_account(
                    name=dialog.result_data["name"],
                    account_type=dialog.result_data["account_type"],
                    opening_balance=dialog.result_data["opening_balance"],
                )
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Menambahkan Akun", str(e))

    def _open_edit_dialog(self, acc: Account) -> None:
        dialog = AccountDialog(account=acc, parent=self)
        if dialog.exec():
            try:
                self.controller.update_account(
                    account_id=acc.id,
                    name=dialog.result_data["name"],
                    account_type=dialog.result_data["account_type"],
                    opening_balance=dialog.result_data["opening_balance"],
                )
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Mengubah Akun", str(e))

    def _toggle_archive(self, account_id: int, currently_archived: bool) -> None:
        try:
            self.controller.archive_account(account_id, not currently_archived)
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            QMessageBox.critical(self, "Gagal Mengubah Status Arsip", str(e))

    def _confirm_delete(self, account_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus Akun",
            "Apakah Anda yakin ingin menghapus akun ini? "
            "Akun dengan riwayat transaksi tidak dapat dihapus dan harus diarsipkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_account(account_id)
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Menghapus Akun", str(e))
