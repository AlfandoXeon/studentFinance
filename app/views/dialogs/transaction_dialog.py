from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.ui.components.currency_line_edit import CurrencyLineEdit
from app.utils.formatters import parse_currency


class TransactionDialog(QDialog):
    """Dialog for creating or editing an income, expense, or transfer transaction."""

    def __init__(
        self,
        accounts: List[Account],
        categories: List[Category],
        transaction: Optional[Transaction] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.accounts = accounts
        self.categories = categories
        self.transaction = transaction

        self.setWindowTitle("Edit Transaksi" if transaction else "Catat Transaksi")
        self.setMinimumWidth(420)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        # Type selector
        self.type_combo = QComboBox()
        self.type_combo.addItem("Pengeluaran (Expense)", "expense")
        self.type_combo.addItem("Pemasukan (Income)", "income")
        self.type_combo.addItem("Pindah Saldo (Transfer)", "transfer")
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form_layout.addRow("Tipe Transaksi:", self.type_combo)

        # Amount with live thousands formatting
        self.amount_input = CurrencyLineEdit()
        self.amount_input.setPlaceholderText("Contoh: 50,000 atau 100,000")
        self.amount_input.returnPressed.connect(self._on_save)
        form_layout.addRow("Nominal (Rp):", self.amount_input)

        # Source Account
        self.account_combo = QComboBox()
        for acc in self.accounts:
            self.account_combo.addItem(f"{acc.name} ({acc.account_type})", acc.id)
        form_layout.addRow("Akun / Sumber:", self.account_combo)

        # Destination Account (for transfers)
        self.to_account_label = QLabel("Akun Tujuan:")
        self.to_account_combo = QComboBox()
        for acc in self.accounts:
            self.to_account_combo.addItem(f"{acc.name} ({acc.account_type})", acc.id)
        form_layout.addRow(self.to_account_label, self.to_account_combo)

        # Category (for income & expense)
        self.category_label = QLabel("Kategori:")
        self.category_combo = QComboBox()
        form_layout.addRow(self.category_label, self.category_combo)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Tanggal:", self.date_input)

        # Description
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Keterangan transaksi (opsional)")
        self.desc_input.returnPressed.connect(self._on_save)
        form_layout.addRow("Catatan / Deskripsi:", self.desc_input)

        layout.addLayout(form_layout)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E16D75; font-size: 12px;")
        layout.addWidget(self.error_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Simpan")
        self.save_btn.setProperty("class", "primary-btn")
        self.save_btn.setDefault(True)
        self.save_btn.setAutoDefault(True)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        # Initial populate
        if self.transaction:
            # Set type
            idx = self.type_combo.findData(self.transaction.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            self.amount_input.set_amount(self.transaction.amount)

            # Set account
            acc_idx = self.account_combo.findData(self.transaction.account_id)
            if acc_idx >= 0:
                self.account_combo.setCurrentIndex(acc_idx)

            if self.transaction.to_account_id:
                to_idx = self.to_account_combo.findData(self.transaction.to_account_id)
                if to_idx >= 0:
                    self.to_account_combo.setCurrentIndex(to_idx)

            # Date
            qdate = QDate.fromString(self.transaction.transaction_date[:10], "yyyy-MM-dd")
            if qdate.isValid():
                self.date_input.setDate(qdate)

            self.desc_input.setText(self.transaction.description or "")

        self._on_type_changed()

        if self.transaction and self.transaction.category_id:
            cat_idx = self.category_combo.findData(self.transaction.category_id)
            if cat_idx >= 0:
                self.category_combo.setCurrentIndex(cat_idx)

    def _on_type_changed(self) -> None:
        t_type = self.type_combo.currentData()
        if t_type == "transfer":
            self.to_account_label.show()
            self.to_account_combo.show()
            self.category_label.hide()
            self.category_combo.hide()
        else:
            self.to_account_label.hide()
            self.to_account_combo.hide()
            self.category_label.show()
            self.category_combo.show()

            self.category_combo.clear()
            filtered = [c for c in self.categories if c.type == t_type and not c.is_archived]
            for c in filtered:
                self.category_combo.addItem(c.name, c.id)

    def _on_save(self) -> None:
        self.error_label.setText("")
        # Validate amount
        try:
            amount = parse_currency(self.amount_input.text())
        except ValueError as e:
            self.error_label.setText(str(e))
            return

        t_type = self.type_combo.currentData()
        source_acc_id = self.account_combo.currentData()
        if not source_acc_id:
            self.error_label.setText("Silakan pilih akun sumber terlebih dahulu.")
            return

        to_acc_id = None
        cat_id = None

        if t_type == "transfer":
            to_acc_id = self.to_account_combo.currentData()
            if not to_acc_id:
                self.error_label.setText("Silakan pilih akun tujuan transfer.")
                return
            if source_acc_id == to_acc_id:
                self.error_label.setText("Akun sumber dan akun tujuan tidak boleh sama.")
                return
        else:
            cat_id = self.category_combo.currentData()
            if not cat_id:
                self.error_label.setText("Silakan pilih kategori transaksi.")
                return

        date_str = self.date_input.date().toString("yyyy-MM-dd")
        desc = self.desc_input.text().strip() or None

        self.result_data = {
            "type": t_type,
            "amount": amount,
            "account_id": source_acc_id,
            "to_account_id": to_acc_id,
            "category_id": cat_id,
            "transaction_date": date_str,
            "description": desc,
        }
        self.accept()
