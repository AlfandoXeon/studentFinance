from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class WelcomeDialog(QDialog):
    """Modal dialog prompting the user for their name upon initial application startup."""

    def __init__(self, icon_path: Optional[Path] = None, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.user_name: str = ""
        self.setWindowTitle("Selamat Datang di Student Finance")
        self.setFixedWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        if self.icon_path and self.icon_path.exists():
            icon_lbl = QLabel()
            pixmap = QPixmap(str(self.icon_path)).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pixmap)
            header_layout.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("Selamat Datang!")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Student Finance - Offline & Pribadi")
        subtitle.setStyleSheet("font-size: 12px; color: #8B9BB4;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Prompt text
        prompt = QLabel("Untuk mempersonalisasi catatan keuangan Anda, silakan masukkan nama Anda:")
        prompt.setWordWrap(True)
        prompt.setStyleSheet("color: #C0C3CB; font-size: 13px;")
        layout.addWidget(prompt)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama Anda (misal: Alfando)")
        self.name_input.returnPressed.connect(self._on_submit)
        layout.addWidget(self.name_input)

        # Error message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E16D75; font-size: 12px;")
        layout.addWidget(self.error_label)

        # Submit button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.submit_btn = QPushButton("Mulai Aplikasi")
        self.submit_btn.setProperty("class", "primary-btn")
        self.submit_btn.setDefault(True)
        self.submit_btn.clicked.connect(self._on_submit)
        btn_layout.addWidget(self.submit_btn)

        layout.addLayout(btn_layout)

    def _on_submit(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Silakan masukkan nama Anda terlebih dahulu.")
            self.name_input.setFocus()
            return

        self.user_name = name
        self.accept()

    def get_name(self) -> str:
        return self.user_name
