from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.controllers.category_controller import CategoryController
from app.models.category import Category
from app.views.dialogs.category_dialog import CategoryDialog


class CategoriesView(QWidget):
    """View for managing income and expense categories."""

    def __init__(
        self,
        controller: CategoryController,
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
        title = QLabel("Daftar Kategori")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Kelola pos anggaran pemasukan dan pengeluaran Anda.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.add_btn = QPushButton("+ Tambah Kategori")
        self.add_btn.setProperty("class", "primary-btn")
        self.add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self.add_btn)

        main_layout.addLayout(header_layout)

        # Tab widget for Expense / Income
        self.tabs = QTabWidget()
        self.expense_table = self._create_table()
        self.income_table = self._create_table()

        self.tabs.addTab(self.expense_table, "Pengeluaran (Expense)")
        self.tabs.addTab(self.income_table, "Pemasukan (Income)")
        self.tabs.currentChanged.connect(self.refresh_data)

        main_layout.addWidget(self.tabs)

    def _create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Nama Kategori", "Tipe", "Status", "Aksi"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        table.setColumnWidth(3, 235)
        table.verticalHeader().setDefaultSectionSize(44)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table

    def refresh_data(self) -> None:
        """Fetch categories and populate active tab table."""
        # Expense
        exp_cats = self.controller.list_categories(cat_type="expense", include_archived=True)
        self._populate_table(self.expense_table, exp_cats)

        # Income
        inc_cats = self.controller.list_categories(cat_type="income", include_archived=True)
        self._populate_table(self.income_table, inc_cats)

    def _populate_table(self, table: QTableWidget, categories: list[Category]) -> None:
        table.setRowCount(len(categories))
        for row_idx, cat in enumerate(categories):
            # Name
            table.setItem(row_idx, 0, QTableWidgetItem(cat.name))

            # Type
            type_str = "Pemasukan" if cat.type == "income" else "Pengeluaran"
            item_type = QTableWidgetItem(type_str)
            item_type.setTextAlignment(Qt.AlignCenter)
            table.setItem(row_idx, 1, item_type)

            # Status
            item_status = QTableWidgetItem("Arsip" if cat.is_archived else "Aktif")
            item_status.setTextAlignment(Qt.AlignCenter)
            table.setItem(row_idx, 2, item_status)

            # Actions
            action_widget = QWidget()
            btn_box = QHBoxLayout(action_widget)
            btn_box.setContentsMargins(4, 2, 4, 2)
            btn_box.setSpacing(6)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(55)
            edit_btn.clicked.connect(lambda checked=False, c=cat: self._open_edit_dialog(c))
            btn_box.addWidget(edit_btn)

            archive_btn = QPushButton("Aktifkan" if cat.is_archived else "Arsipkan")
            archive_btn.setFixedWidth(80)
            archive_btn.clicked.connect(
                lambda checked=False, c_id=cat.id, is_arch=cat.is_archived: self._toggle_archive(c_id, is_arch)
            )
            btn_box.addWidget(archive_btn)

            del_btn = QPushButton("Hapus")
            del_btn.setFixedWidth(65)
            del_btn.setProperty("class", "danger-btn")
            del_btn.clicked.connect(lambda checked=False, c_id=cat.id: self._confirm_delete(c_id))
            btn_box.addWidget(del_btn)

            table.setCellWidget(row_idx, 3, action_widget)

    def _open_add_dialog(self) -> None:
        default_type = "expense" if self.tabs.currentIndex() == 0 else "income"
        dialog = CategoryDialog(default_type=default_type, parent=self)
        if dialog.exec():
            try:
                self.controller.create_category(
                    name=dialog.result_data["name"],
                    cat_type=dialog.result_data["type"],
                )
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Menambahkan Kategori", str(e))

    def _open_edit_dialog(self, cat: Category) -> None:
        dialog = CategoryDialog(category=cat, parent=self)
        if dialog.exec():
            try:
                self.controller.update_category(
                    category_id=cat.id,
                    name=dialog.result_data["name"],
                )
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Mengubah Kategori", str(e))

    def _toggle_archive(self, category_id: int, currently_archived: bool) -> None:
        try:
            self.controller.archive_category(category_id, not currently_archived)
            self.refresh_data()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            QMessageBox.critical(self, "Gagal Mengubah Status Arsip", str(e))

    def _confirm_delete(self, category_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus Kategori",
            "Apakah Anda yakin ingin menghapus kategori ini? "
            "Kategori yang telah digunakan dalam transaksi atau anggaran harus diarsipkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_category(category_id)
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Menghapus Kategori", str(e))
