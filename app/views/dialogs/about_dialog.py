from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.config.settings import AppSettings


class AboutDialog(QDialog):
    """Dialog displaying application information, version, and developer details."""

    def __init__(self, settings: Optional[AppSettings] = None, parent=None):
        super().__init__(parent)
        self.settings = settings or AppSettings()
        self.setWindowTitle("Tentang Student Finance")
        self.setFixedWidth(460)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header with Logo & App Info
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        if self.settings.icon_path.exists():
            icon_lbl = QLabel()
            pixmap = QPixmap(str(self.settings.icon_path)).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pixmap)
            header_layout.addWidget(icon_lbl)

        info_box = QVBoxLayout()
        info_box.setSpacing(4)

        app_title = QLabel(self.settings.app_name)
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        info_box.addWidget(app_title)

        version_badge = QLabel(f"Versi {self.settings.version} • Offline-First")
        version_badge.setStyleSheet("font-size: 12px; color: #8B9BB4; font-weight: 500;")
        info_box.addWidget(version_badge)

        header_layout.addLayout(info_box)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Description
        desc_lbl = QLabel(
            "Aplikasi manajemen keuangan pribadi yang dirancang khusus untuk mahasiswa. "
            "Bekerja 100% secara offline tanpa pelacakan data, "
            "menjaga privasi finansial Anda sepenuhnya di perangkat lokal."
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #C0C3CB; font-size: 13px; line-height: 1.4;")
        layout.addWidget(desc_lbl)

        # Developer Info Box
        dev_card = QFrame()
        dev_card.setStyleSheet(
            "background-color: #202228; border: 1px solid #333640; border-radius: 8px; padding: 12px;"
        )
        dev_layout = QVBoxLayout(dev_card)
        dev_layout.setSpacing(6)

        dev_title = QLabel("Informasi Pengembang")
        dev_title.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #8B9BB4; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        dev_layout.addWidget(dev_title)

        dev_name = QLabel(f"Developer: <b>{self.settings.developer_name}</b>")
        dev_name.setStyleSheet("font-size: 13px; color: #F2F3F5;")
        dev_layout.addWidget(dev_name)

        dev_link = QLabel(
            f'Website: <a href="{self.settings.developer_website}" style="color: #61AFEF; text-decoration: underline;">'
            f"{self.settings.developer_website}</a>"
        )
        dev_link.setStyleSheet("font-size: 13px; color: #F2F3F5;")
        dev_link.setOpenExternalLinks(True)
        dev_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        dev_layout.addWidget(dev_link)

        layout.addWidget(dev_card)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.close_btn = QPushButton("Tutup")
        self.close_btn.setProperty("class", "primary-btn")
        self.close_btn.setDefault(True)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)
