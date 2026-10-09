from __future__ import annotations

from typing import List, Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.models.category import Category
from app.ui.components.currency_line_edit import CurrencyLineEdit
from app.utils.formatters import parse_currency


class BudgetDialog(QDialog):
    """Dialog for setting a monthly expense budget."""

    def __init__(
        self,
        categories: List[Category],
        initial_category_id: Optional[int] = None,
        initial_amount: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.categories = categories
        self.initial_category_id = initial_category_id
        self.initial_amount = initial_amount

        self.setWindowTitle("Atur Anggaran Bulanan")
        self.setMinimumWidth(380)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.category_combo = QComboBox()
        for cat in self.categories:
            if cat.type == "expense" and not cat.is_archived:
                self.category_combo.addItem(cat.name, cat.id)
        form_layout.addRow("Kategori Pengeluaran:", self.category_combo)

        self.amount_input = CurrencyLineEdit()
        self.amount_input.setPlaceholderText("Batas anggaran, contoh: 500,000")
        if self.initial_amount > 0:
            self.amount_input.set_amount(self.initial_amount)
        self.amount_input.returnPressed.connect(self._on_save)
        form_layout.addRow("Batas Anggaran (Rp):", self.amount_input)

        layout.addLayout(form_layout)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E16D75; font-size: 12px;")
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Simpan Anggaran")
        self.save_btn.setProperty("class", "primary-btn")
        self.save_btn.setDefault(True)
        self.save_btn.setAutoDefault(True)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        if self.initial_category_id:
            idx = self.category_combo.findData(self.initial_category_id)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
                self.category_combo.setEnabled(False)

    def _on_save(self) -> None:
        self.error_label.setText("")
        cat_id = self.category_combo.currentData()
        if not cat_id:
            self.error_label.setText("Silakan pilih kategori pengeluaran.")
            return

        try:
            amount = parse_currency(self.amount_input.text())
        except ValueError as e:
            self.error_label.setText(str(e))
            return

        self.result_data = {
            "category_id": cat_id,
            "amount": amount,
        }
        self.accept()
