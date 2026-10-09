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

from app.models.category import Category


class CategoryDialog(QDialog):
    """Dialog for creating or editing a category."""

    def __init__(self, category: Optional[Category] = None, default_type: str = "expense", parent=None):
        super().__init__(parent)
        self.category = category
        self.default_type = default_type
        self.setWindowTitle("Edit Kategori" if category else "Tambah Kategori Baru")
        self.setMinimumWidth(360)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama kategori")
        self.name_input.returnPressed.connect(self._on_save)
        form_layout.addRow("Nama Kategori:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Pengeluaran (Expense)", "expense")
        self.type_combo.addItem("Pemasukan (Income)", "income")
        form_layout.addRow("Tipe Kategori:", self.type_combo)

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

        if self.category:
            self.name_input.setText(self.category.name)
            idx = self.type_combo.findData(self.category.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            self.type_combo.setEnabled(False)  # Category type should remain immutable when editing
        else:
            idx = self.type_combo.findData(self.default_type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)

    def _on_save(self) -> None:
        self.error_label.setText("")
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Nama kategori tidak boleh kosong.")
            return

        self.result_data = {
            "name": name,
            "type": self.type_combo.currentData(),
        }
        self.accept()
