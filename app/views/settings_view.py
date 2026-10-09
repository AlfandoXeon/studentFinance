from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.controllers.settings_controller import SettingsController
from app.views.dialogs.about_dialog import AboutDialog


class SettingsView(QWidget):
    """View for application configuration, database snapshots, and user profile management."""

    def __init__(
        self,
        controller: SettingsController,
        on_data_restored: Optional[Callable] = None,
        on_user_name_changed: Optional[Callable[[str], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.on_data_restored = on_data_restored
        self.on_user_name_changed = on_user_name_changed
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(20)

        # Header
        title_box = QVBoxLayout()
        title = QLabel("Pengaturan Aplikasi")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Kelola profil pengguna, cadangan data lokal (backup), dan informasi sistem.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        main_layout.addLayout(title_box)

        # 1. User Profile Card
        profile_card = QFrame()
        profile_card.setProperty("class", "card")
        profile_box = QVBoxLayout(profile_card)
        profile_box.setSpacing(12)

        p_title = QLabel("Profil Pengguna")
        p_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #F2F3F5;")
        profile_box.addWidget(p_title)

        p_desc = QLabel("Nama pengguna digunakan untuk sapaan pada dashboard dan identitas pembukuan keuangan.")
        p_desc.setStyleSheet("font-size: 12px; color: #8B9BB4;")
        profile_box.addWidget(p_desc)

        p_form_layout = QHBoxLayout()
        p_form_layout.setSpacing(10)

        p_lbl = QLabel("Nama Pengguna:")
        p_lbl.setStyleSheet("font-weight: 500; color: #F2F3F5;")
        p_form_layout.addWidget(p_lbl)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Masukkan nama Anda (misal: Alfando)")
        current_name = self.controller.get_user_name() or ""
        self.name_input.setText(current_name)
        self.name_input.returnPressed.connect(self._save_user_name)
        p_form_layout.addWidget(self.name_input, 1)

        self.btn_save_name = QPushButton("Simpan Nama")
        self.btn_save_name.setProperty("class", "primary-btn")
        self.btn_save_name.setDefault(True)
        self.btn_save_name.clicked.connect(self._save_user_name)
        p_form_layout.addWidget(self.btn_save_name)

        profile_box.addLayout(p_form_layout)

        self.name_feedback_lbl = QLabel("")
        self.name_feedback_lbl.setStyleSheet("font-size: 12px;")
        profile_box.addWidget(self.name_feedback_lbl)

        main_layout.addWidget(profile_card)

        # 2. Backup & Restore Card
        backup_card = QFrame()
        backup_card.setProperty("class", "card")
        backup_box = QVBoxLayout(backup_card)
        backup_box.setSpacing(14)

        b_header = QHBoxLayout()
        b_title = QLabel("Cadangan Database (Backup & Restore)")
        b_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #F2F3F5;")
        b_header.addWidget(b_title)
        b_header.addStretch()

        self.btn_backup_now = QPushButton("Buat Cadangan Baru (Backup)")
        self.btn_backup_now.setProperty("class", "primary-btn")
        self.btn_backup_now.clicked.connect(self._create_backup)
        b_header.addWidget(self.btn_backup_now)

        self.btn_restore_file = QPushButton("Pulihkan dari File Lain...")
        self.btn_restore_file.clicked.connect(self._restore_from_file_dialog)
        b_header.addWidget(self.btn_restore_file)

        backup_box.addLayout(b_header)

        # Table of backups
        self.table_backups = QTableWidget()
        self.table_backups.setColumnCount(4)
        self.table_backups.setHorizontalHeaderLabels(
            [
                "Nama File",
                "Ukuran",
                "Tanggal Dibuat",
                "Aksi",
            ]
        )
        self.table_backups.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_backups.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_backups.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_backups.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_backups.setColumnWidth(3, 110)
        self.table_backups.verticalHeader().setDefaultSectionSize(44)
        self.table_backups.verticalHeader().setVisible(False)
        self.table_backups.setAlternatingRowColors(True)
        self.table_backups.setEditTriggers(QTableWidget.NoEditTriggers)

        backup_box.addWidget(self.table_backups)
        main_layout.addWidget(backup_card)

        # 3. System Info & About Card
        info_card = QFrame()
        info_card.setProperty("class", "card")
        info_box = QVBoxLayout(info_card)
        info_box.setSpacing(12)

        info_header = QHBoxLayout()
        info_title = QLabel("Tentang Aplikasi & Pengembang")
        info_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #F2F3F5;")
        info_header.addWidget(info_title)
        info_header.addStretch()

        self.btn_show_about = QPushButton("Buka Dialog Tentang...")
        self.btn_show_about.clicked.connect(self._open_about_dialog)
        info_header.addWidget(self.btn_show_about)
        info_box.addLayout(info_header)

        sys_info = self.controller.get_system_info()
        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Aplikasi:", QLabel(sys_info["app_name"]))
        form.addRow("Versi:", QLabel(f"v{sys_info['version']} (Offline Mode)"))

        dev_lbl = QLabel(f"<b>{sys_info['developer_name']}</b>")
        dev_lbl.setStyleSheet("color: #F2F3F5;")
        form.addRow("Pengembang:", dev_lbl)

        web_lbl = QLabel(
            f'<a href="{sys_info["developer_website"]}" style="color: #61AFEF; text-decoration: underline;">'
            f"{sys_info['developer_website']}</a>"
        )
        web_lbl.setOpenExternalLinks(True)
        web_lbl.setTextInteractionFlags(Qt.TextBrowserInteraction)
        form.addRow("Website Pengembang:", web_lbl)

        form.addRow("Mata Uang:", QLabel(sys_info["currency"]))
        form.addRow("Mesin Penyimpanan:", QLabel(sys_info["storage_engine"]))
        form.addRow("Lokasi Database:", QLabel(sys_info["db_path"]))
        form.addRow("Folder Backup:", QLabel(sys_info["backup_dir"]))
        form.addRow("Folder Logs:", QLabel(sys_info["logs_dir"]))
        info_box.addLayout(form)

        # Security notice
        sec_notice = QLabel(
            "Pemberitahuan Keamanan: Aplikasi ini bekerja sepenuhnya offline. "
            "Data tersimpan dalam file SQLite lokal tanpa enkripsi bawaan. "
            "Jaga keamanan fisik perangkat Anda dan lakukan pencadangan berkala."
        )
        sec_notice.setWordWrap(True)
        sec_notice.setStyleSheet(
            "padding: 8px; background-color: #202125; border-radius: 4px; font-size: 11px; color: #A5A8B0;"
        )
        info_box.addWidget(sec_notice)

        main_layout.addWidget(info_card)

    def _save_user_name(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            self.name_feedback_lbl.setText("Nama pengguna tidak boleh kosong.")
            self.name_feedback_lbl.setStyleSheet("color: #E16D75; font-size: 12px;")
            return

        try:
            saved_name = self.controller.update_user_name(name)
            self.name_input.setText(saved_name)
            self.name_feedback_lbl.setText(f"Nama pengguna berhasil disimpan sebagai '{saved_name}'.")
            self.name_feedback_lbl.setStyleSheet("color: #55B987; font-size: 12px;")
            if self.on_user_name_changed:
                self.on_user_name_changed(saved_name)
        except Exception as e:
            self.name_feedback_lbl.setText(f"Gagal menyimpan: {e}")
            self.name_feedback_lbl.setStyleSheet("color: #E16D75; font-size: 12px;")

    def _open_about_dialog(self) -> None:
        dlg = AboutDialog(self.controller.context.settings, parent=self)
        dlg.exec()

    def refresh_data(self) -> None:
        """Refresh list of available backup files and current user name."""
        current_name = self.controller.get_user_name() or ""
        self.name_input.setText(current_name)
        self.name_feedback_lbl.setText("")

        backups = self.controller.list_backups()
        self.table_backups.setRowCount(len(backups))

        for row_idx, file_path in enumerate(backups):
            # Filename
            self.table_backups.setItem(row_idx, 0, QTableWidgetItem(file_path.name))

            # Size
            size_kb = file_path.stat().st_size / 1024
            item_size = QTableWidgetItem(f"{size_kb:.1f} KB")
            item_size.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_backups.setItem(row_idx, 1, item_size)

            # Date
            dt = datetime.fromtimestamp(file_path.stat().st_mtime)
            item_date = QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S"))
            item_date.setTextAlignment(Qt.AlignCenter)
            self.table_backups.setItem(row_idx, 2, item_date)

            # Action button: Pulihkan
            restore_btn = QPushButton("Pulihkan")
            restore_btn.setFixedWidth(85)
            restore_btn.clicked.connect(lambda checked=False, p=file_path: self._confirm_restore(p))
            self.table_backups.setCellWidget(row_idx, 3, restore_btn)

    def _create_backup(self) -> None:
        try:
            path = self.controller.create_backup()
            self.refresh_data()
            QMessageBox.information(
                self,
                "Cadangan Berhasil",
                f"Database berhasil dicadangkan ke file:\n{path.name}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Gagal Mencadangkan", str(e))

    def _confirm_restore(self, backup_path: Path) -> None:
        reply = QMessageBox.warning(
            self,
            "Konfirmasi Pemulihan Database",
            f"Apakah Anda yakin ingin memulihkan database dari file '{backup_path.name}'?\n\n"
            "Data aktif saat ini akan digantikan oleh isi file cadangan. "
            "Snapshot pemulihan otomatis akan dibuat terlebih dahulu untuk keamanan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._execute_restore(backup_path)

    def _restore_from_file_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Cadangan SQLite", "", "Database Files (*.db *.sqlite);;All Files (*)"
        )
        if not file_path:
            return
        self._confirm_restore(Path(file_path))

    def _execute_restore(self, backup_path: Path) -> None:
        try:
            recovery_path = self.controller.restore_backup(backup_path)
            self.refresh_data()
            if self.on_data_restored:
                self.on_data_restored()
            QMessageBox.information(
                self,
                "Pemulihan Sukses",
                f"Database berhasil dipulihkan dari:\n{backup_path.name}\n\n"
                f"Snapshot darurat sebelum pemulihan disimpan di:\n{recovery_path.name}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Gagal Memulihkan Database", str(e))
