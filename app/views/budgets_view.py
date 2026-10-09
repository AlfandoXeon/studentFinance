from __future__ import annotations

from datetime import date
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.controllers.budget_controller import BudgetController
from app.services.budget_service import BudgetProgress
from app.utils.formatters import ID_MONTHS, format_currency
from app.views.dialogs.budget_dialog import BudgetDialog


class BudgetsView(QWidget):
    """View for managing monthly category budgets and monitoring utilization."""

    def __init__(
        self,
        controller: BudgetController,
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

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Anggaran Pengeluaran")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Tetapkan batas pengeluaran bulanan per kategori untuk mengontrol gaya hidup.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Month & Year selector
        self.month_combo = QComboBox()
        for m_idx in range(1, 13):
            self.month_combo.addItem(ID_MONTHS[m_idx], m_idx)
        cur_month = date.today().month
        self.month_combo.setCurrentIndex(cur_month - 1)
        self.month_combo.currentIndexChanged.connect(self.refresh_data)
        header_layout.addWidget(self.month_combo)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2050)
        self.year_spin.setValue(date.today().year)
        self.year_spin.valueChanged.connect(self.refresh_data)
        header_layout.addWidget(self.year_spin)

        self.add_btn = QPushButton("+ Atur Anggaran")
        self.add_btn.setProperty("class", "primary-btn")
        self.add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self.add_btn)

        main_layout.addLayout(header_layout)

        # Overview summary card
        self.summary_card = QFrame()
        self.summary_card.setProperty("class", "card")
        summary_layout = QHBoxLayout(self.summary_card)

        self.lbl_total_budget = QLabel("Total: Rp 0")
        self.lbl_total_budget.setStyleSheet("font-size: 14px; font-weight: bold;")
        summary_layout.addWidget(self.lbl_total_budget)

        self.lbl_total_used = QLabel("Terpakai: Rp 0")
        self.lbl_total_used.setStyleSheet("font-size: 14px; font-weight: bold; color: #E6B566;")
        summary_layout.addWidget(self.lbl_total_used)

        self.lbl_total_remaining = QLabel("Sisa: Rp 0")
        self.lbl_total_remaining.setStyleSheet("font-size: 14px; font-weight: bold; color: #55B987;")
        summary_layout.addWidget(self.lbl_total_remaining)

        main_layout.addWidget(self.summary_card)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Kategori",
                "Batas Anggaran",
                "Terpakai",
                "Sisa",
                "Persentase",
                "Status",
                "Aksi",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 150)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 150)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table)

    def refresh_data(self) -> None:
        """Fetch budget progress for selected period and update table."""
        year = self.year_spin.value()
        month = self.month_combo.currentData()

        # Update summary card
        summary = self.controller.get_total_summary(year, month)
        self.lbl_total_budget.setText(f"Total Anggaran: {format_currency(summary['total_budget'])}")
        self.lbl_total_used.setText(f"Terpakai: {format_currency(summary['total_used'])}")
        rem = summary["total_remaining"]
        self.lbl_total_remaining.setText(f"Sisa: {format_currency(rem)}")
        if rem < 0:
            self.lbl_total_remaining.setStyleSheet("font-size: 14px; font-weight: bold; color: #E16D75;")
        else:
            self.lbl_total_remaining.setStyleSheet("font-size: 14px; font-weight: bold; color: #55B987;")

        progress_list = self.controller.get_budget_progress(year, month)
        self.table.setRowCount(len(progress_list))

        for row_idx, item in enumerate(progress_list):
            # Category
            self.table.setItem(row_idx, 0, QTableWidgetItem(item.category_name))

            # Budget
            item_budget = QTableWidgetItem(format_currency(item.budget_amount))
            item_budget.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 1, item_budget)

            # Used
            item_used = QTableWidgetItem(format_currency(item.used_amount))
            item_used.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 2, item_used)

            # Remaining
            item_rem = QTableWidgetItem(format_currency(item.remaining_amount))
            item_rem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if item.remaining_amount < 0:
                item_rem.setForeground(Qt.GlobalColor.red)
            else:
                item_rem.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row_idx, 3, item_rem)

            # Percentage Progress bar cell
            bar_widget = QWidget()
            bar_layout = QHBoxLayout(bar_widget)
            bar_layout.setContentsMargins(6, 2, 6, 2)
            pbar = QProgressBar()
            pbar.setRange(0, 100)
            pbar.setValue(min(100, int(item.percentage)))
            pbar.setFormat(f"{item.percentage:.1f}%")
            if item.is_exceeded:
                pbar.setStyleSheet("QProgressBar::chunk { background-color: #E16D75; }")
            elif item.is_warning:
                pbar.setStyleSheet("QProgressBar::chunk { background-color: #E6B566; }")
            else:
                pbar.setStyleSheet("QProgressBar::chunk { background-color: #55B987; }")
            bar_layout.addWidget(pbar)
            self.table.setCellWidget(row_idx, 4, bar_widget)

            # Status
            if item.is_exceeded:
                status_str = "Over Budget"
                status_color = Qt.GlobalColor.red
            elif item.is_warning:
                status_str = "Peringatan (>=80%)"
                status_color = Qt.GlobalColor.yellow
            else:
                status_str = "Aman"
                status_color = Qt.GlobalColor.green
            item_status = QTableWidgetItem(status_str)
            item_status.setTextAlignment(Qt.AlignCenter)
            item_status.setForeground(status_color)
            self.table.setItem(row_idx, 5, item_status)

            # Actions
            action_widget = QWidget()
            btn_box = QHBoxLayout(action_widget)
            btn_box.setContentsMargins(4, 2, 4, 2)
            btn_box.setSpacing(6)

            edit_btn = QPushButton("Ubah")
            edit_btn.setFixedWidth(55)
            edit_btn.clicked.connect(lambda checked=False, p=item: self._open_edit_dialog(p))
            btn_box.addWidget(edit_btn)

            del_btn = QPushButton("Hapus")
            del_btn.setFixedWidth(65)
            del_btn.setProperty("class", "danger-btn")
            del_btn.clicked.connect(lambda checked=False, b_id=item.budget_id: self._confirm_delete(b_id))
            btn_box.addWidget(del_btn)

            self.table.setCellWidget(row_idx, 6, action_widget)

    def _open_add_dialog(self) -> None:
        categories = self.controller.get_expense_categories()
        if not categories:
            QMessageBox.warning(self, "Peringatan", "Tidak ada kategori pengeluaran yang tersedia.")
            return

        dialog = BudgetDialog(categories=categories, parent=self)
        if dialog.exec():
            try:
                year = self.year_spin.value()
                month = self.month_combo.currentData()
                self.controller.set_budget(
                    category_id=dialog.result_data["category_id"],
                    amount=dialog.result_data["amount"],
                    year=year,
                    month=month,
                )
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Mengatur Anggaran", str(e))

    def _open_edit_dialog(self, item: BudgetProgress) -> None:
        categories = self.controller.get_expense_categories()
        dialog = BudgetDialog(
            categories=categories,
            initial_category_id=item.category_id,
            initial_amount=item.budget_amount,
            parent=self,
        )
        if dialog.exec():
            try:
                year = self.year_spin.value()
                month = self.month_combo.currentData()
                self.controller.set_budget(
                    category_id=item.category_id,
                    amount=dialog.result_data["amount"],
                    year=year,
                    month=month,
                )
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Mengubah Anggaran", str(e))

    def _confirm_delete(self, budget_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus Anggaran",
            "Apakah Anda yakin ingin menghapus anggaran untuk kategori ini?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_budget(budget_id)
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Menghapus Anggaran", str(e))
