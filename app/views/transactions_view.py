from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
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

from app.controllers.transaction_controller import TransactionController
from app.models.transaction import Transaction
from app.utils.formatters import format_currency, format_date_display
from app.views.dialogs.transaction_dialog import TransactionDialog


class TransactionsView(QWidget):
    """View for browsing, filtering, adding, editing, and deleting transactions."""

    def __init__(
        self,
        controller: TransactionController,
        on_data_changed: Optional[Callable] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.controller = controller
        self.on_data_changed = on_data_changed
        self.current_transactions = []
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header with actions
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Daftar Transaksi")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Kelola pemasukan, pengeluaran, dan transfer saldo antar rekening.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.add_btn = QPushButton("+ Tambah Transaksi")
        self.add_btn.setProperty("class", "primary-btn")
        self.add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self.add_btn)

        self.export_btn = QPushButton("Ekspor CSV")
        self.export_btn.clicked.connect(self._export_csv)
        header_layout.addWidget(self.export_btn)

        main_layout.addLayout(header_layout)

        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari catatan / keterangan...")
        self.search_input.returnPressed.connect(self.refresh_data)
        filter_layout.addWidget(self.search_input, 2)

        # Type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("Semua Tipe", "")
        self.type_filter.addItem("Pengeluaran", "expense")
        self.type_filter.addItem("Pemasukan", "income")
        self.type_filter.addItem("Transfer", "transfer")
        self.type_filter.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.type_filter, 1)

        # Account filter
        self.account_filter = QComboBox()
        self.account_filter.addItem("Semua Akun", None)
        self.account_filter.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.account_filter, 1)

        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItem("Semua Kategori", None)
        self.category_filter.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.category_filter, 1)

        # Date range checkbox/filters
        date_box = QHBoxLayout()
        date_box.setSpacing(6)
        date_box.addWidget(QLabel("Dari:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.refresh_data)
        date_box.addWidget(self.date_from)

        date_box.addWidget(QLabel("Sampai:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.refresh_data)
        date_box.addWidget(self.date_to)

        filter_layout.addLayout(date_box)

        self.reset_filter_btn = QPushButton("Reset")
        self.reset_filter_btn.clicked.connect(self._reset_filters)
        filter_layout.addWidget(self.reset_filter_btn)

        main_layout.addLayout(filter_layout)

        # Transactions table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Tanggal",
                "Tipe",
                "Nominal",
                "Akun Asal",
                "Akun Tujuan / Kategori",
                "Keterangan",
                "Aksi",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 150)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        main_layout.addWidget(self.table)

    def _populate_filter_dropdowns(self) -> None:
        """Update accounts and categories in filter combos while retaining current selection."""
        cur_acc = self.account_filter.currentData()
        self.account_filter.blockSignals(True)
        self.account_filter.clear()
        self.account_filter.addItem("Semua Akun", None)
        for a in self.controller.get_accounts(include_archived=True):
            self.account_filter.addItem(a.name, a.id)
        if cur_acc:
            idx = self.account_filter.findData(cur_acc)
            if idx >= 0:
                self.account_filter.setCurrentIndex(idx)
        self.account_filter.blockSignals(False)

        cur_cat = self.category_filter.currentData()
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("Semua Kategori", None)
        for c in self.controller.get_categories(include_archived=True):
            self.category_filter.addItem(f"{c.name} ({'Masuk' if c.type == 'income' else 'Keluar'})", c.id)
        if cur_cat:
            c_idx = self.category_filter.findData(cur_cat)
            if c_idx >= 0:
                self.category_filter.setCurrentIndex(c_idx)
        self.category_filter.blockSignals(False)

    def _reset_filters(self) -> None:
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.account_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.refresh_data()

    def refresh_data(self) -> None:
        """Fetch transactions matching current active filters and render table."""
        self._populate_filter_dropdowns()

        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        t_type = self.type_filter.currentData() or None
        acc_id = self.account_filter.currentData()
        cat_id = self.category_filter.currentData()
        query = self.search_input.text().strip() or None

        self.current_transactions = self.controller.list_transactions(
            start_date=start_date,
            end_date=end_date,
            account_id=acc_id,
            category_id=cat_id,
            transaction_type=t_type,
            search_query=query,
        )

        accounts = {a.id: a.name for a in self.controller.get_accounts(include_archived=True)}
        categories = {c.id: c.name for c in self.controller.get_categories(include_archived=True)}

        self.table.setRowCount(len(self.current_transactions))
        for row_idx, t in enumerate(self.current_transactions):
            # Date
            item_date = QTableWidgetItem(format_date_display(t.transaction_date, short=True))
            item_date.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item_date)

            # Type
            type_label = "Pengeluaran"
            if t.type == "income":
                type_label = "Pemasukan"
            elif t.type == "transfer":
                type_label = "Transfer"
            item_type = QTableWidgetItem(type_label)
            item_type.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_type)

            # Amount
            item_amt = QTableWidgetItem(format_currency(t.amount))
            item_amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if t.type == "income":
                item_amt.setForeground(Qt.GlobalColor.green)
            elif t.type == "expense":
                item_amt.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 2, item_amt)

            # Source Account
            acc_name = accounts.get(t.account_id, f"Akun #{t.account_id}")
            self.table.setItem(row_idx, 3, QTableWidgetItem(acc_name))

            # Destination Account / Category
            if t.type == "transfer":
                dest_name = accounts.get(t.to_account_id, f"Akun #{t.to_account_id}")
                dest_str = f"-> {dest_name}"
            else:
                dest_str = categories.get(t.category_id, "-")
            self.table.setItem(row_idx, 4, QTableWidgetItem(dest_str))

            # Description
            self.table.setItem(row_idx, 5, QTableWidgetItem(t.description or ""))

            # Action buttons cell (Edit, Hapus)
            action_widget = QWidget()
            btn_box = QHBoxLayout(action_widget)
            btn_box.setContentsMargins(4, 2, 4, 2)
            btn_box.setSpacing(6)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(55)
            edit_btn.clicked.connect(lambda checked=False, txn=t: self._open_edit_dialog(txn))
            btn_box.addWidget(edit_btn)

            del_btn = QPushButton("Hapus")
            del_btn.setFixedWidth(65)
            del_btn.setProperty("class", "danger-btn")
            del_btn.clicked.connect(lambda checked=False, txn_id=t.id: self._confirm_delete(txn_id))
            btn_box.addWidget(del_btn)

            self.table.setCellWidget(row_idx, 6, action_widget)

    def _open_add_dialog(self) -> None:
        accounts = self.controller.get_accounts(include_archived=False)
        if not accounts:
            QMessageBox.warning(self, "Peringatan", "Buat akun terlebih dahulu sebelum mencatat transaksi.")
            return

        categories = self.controller.get_categories(include_archived=False)
        dialog = TransactionDialog(accounts=accounts, categories=categories, parent=self)
        if dialog.exec():
            try:
                self.controller.create_transaction(dialog.result_data)
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Mencatat Transaksi", str(e))

    def _open_edit_dialog(self, txn: Transaction) -> None:
        accounts = self.controller.get_accounts(include_archived=True)
        categories = self.controller.get_categories(include_archived=True)
        dialog = TransactionDialog(accounts=accounts, categories=categories, transaction=txn, parent=self)
        if dialog.exec():
            try:
                txn.type = dialog.result_data["type"]
                txn.amount = dialog.result_data["amount"]
                txn.account_id = dialog.result_data["account_id"]
                txn.to_account_id = dialog.result_data["to_account_id"]
                txn.category_id = dialog.result_data["category_id"]
                txn.transaction_date = dialog.result_data["transaction_date"]
                txn.description = dialog.result_data["description"]
                self.controller.update_transaction(txn)
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Mengubah Transaksi", str(e))

    def _confirm_delete(self, txn_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Apakah Anda yakin ingin menghapus transaksi ini? Tindakan ini akan memperbarui saldo akun terkait.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_transaction(txn_id)
                self.refresh_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Gagal Menghapus Transaksi", str(e))

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "transaksi.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            start_date = self.date_from.date().toString("yyyy-MM-dd")
            end_date = self.date_to.date().toString("yyyy-MM-dd")
            t_type = self.type_filter.currentData() or None
            acc_id = self.account_filter.currentData()
            cat_id = self.category_filter.currentData()

            csv_text = self.controller.export_csv(
                start_date=start_date,
                end_date=end_date,
                account_id=acc_id,
                category_id=cat_id,
                transaction_type=t_type,
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_text)
            QMessageBox.information(self, "Ekspor Berhasil", f"Data transaksi berhasil diekspor ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Gagal Ekspor CSV", str(e))
