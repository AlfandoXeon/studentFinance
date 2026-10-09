from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.models.account import Account
from app.ui.components.currency_line_edit import CurrencyLineEdit
from app.utils.formatters import parse_currency


class AccountDialog(QDialog):
    """Dialog for creating or editing an account."""

    def __init__(self, account: Optional[Account] = None, parent=None):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle("Edit Akun" if account else "Tambah Akun Baru")
        self.setMinimumWidth(380)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Misal: Bank BCA, Dompet Tunai, Gopay")
        self.name_input.returnPressed.connect(self._on_save)
        form_layout.addRow("Nama Akun:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Tunai (Cash)", "cash")
        self.type_combo.addItem("Rekening Bank", "bank")
        self.type_combo.addItem("Dompet Digital (E-Wallet)", "e_wallet")
        form_layout.addRow("Tipe Akun:", self.type_combo)

        self.balance_input = CurrencyLineEdit()
        self.balance_input.setPlaceholderText("0")
        self.balance_input.returnPressed.connect(self._on_save)
        form_layout.addRow("Saldo Awal (Rp):", self.balance_input)

        layout.addLayout(form_layout)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E16D75; font-size: 12px;")
        layout.addWidget(self.error_label)

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

        if self.account:
            self.name_input.setText(self.account.name)
            idx = self.type_combo.findData(self.account.account_type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            self.balance_input.set_amount(self.account.opening_balance)

    def _on_save(self) -> None:
        self.error_label.setText("")
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Nama akun tidak boleh kosong.")
            return

        bal_text = self.balance_input.text().strip()
        if not bal_text or bal_text == "0":
            opening_balance = 0
        else:
            try:
                opening_balance = parse_currency(bal_text)
            except ValueError as e:
                self.error_label.setText(str(e))
                return

        self.result_data = {
            "name": name,
            "account_type": self.type_combo.currentData(),
            "opening_balance": opening_balance,
        }
        self.accept()
