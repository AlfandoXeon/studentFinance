from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.controllers.dashboard_controller import DashboardController
from app.utils.formatters import format_currency, format_date_display


class MetricCard(QFrame):
    """Reusable card for displaying high-level financial metrics."""

    def __init__(self, title: str, initial_value: str = "Rp 0", status: str = "neutral", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "subtitle")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(initial_value)
        self.value_label.setProperty("class", "metric-value")
        self.set_status(status)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def set_status(self, status: str) -> None:
        if status == "success":
            self.value_label.setStyleSheet("color: #55B987; font-size: 22px; font-weight: bold;")
        elif status == "danger":
            self.value_label.setStyleSheet("color: #E16D75; font-size: 22px; font-weight: bold;")
        elif status == "warning":
            self.value_label.setStyleSheet("color: #E6B566; font-size: 22px; font-weight: bold;")
        else:
            self.value_label.setStyleSheet("color: #F2F3F5; font-size: 22px; font-weight: bold;")


class DashboardView(QWidget):
    """Dashboard view presenting key financial indicators and recent transactions."""

    def __init__(self, controller: DashboardController, on_record_transaction: Optional[Callable] = None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.on_record_transaction = on_record_transaction
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(20)

        # Header section
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        self.page_title = QLabel("Ikhtisar Keuangan Mahasiswa")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        self.subtitle = QLabel("Pantau saldo dompet, arus kas bulanan, dan batas aman belanja harian.")
        self.subtitle.setProperty("class", "subtitle")
        title_box.addWidget(self.page_title)
        title_box.addWidget(self.subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.add_txn_btn = QPushButton("+ Catat Transaksi")
        self.add_txn_btn.setProperty("class", "primary-btn")
        if self.on_record_transaction:
            self.add_txn_btn.clicked.connect(self.on_record_transaction)
        header_layout.addWidget(self.add_txn_btn)

        main_layout.addLayout(header_layout)

        # Metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        self.card_total_balance = MetricCard("Total Saldo Aktif", "Rp 0")
        self.card_month_income = MetricCard("Pemasukan Bulan Ini", "Rp 0", status="success")
        self.card_month_expense = MetricCard("Pengeluaran Bulan Ini", "Rp 0", status="danger")
        self.card_month_net = MetricCard("Arus Kas Bersih", "Rp 0")

        metrics_layout.addWidget(self.card_total_balance)
        metrics_layout.addWidget(self.card_month_income)
        metrics_layout.addWidget(self.card_month_expense)
        metrics_layout.addWidget(self.card_month_net)

        main_layout.addLayout(metrics_layout)

        # Middle row: Budget & Survival summary cards
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(16)

        # Budget card
        self.budget_card = QFrame()
        self.budget_card.setProperty("class", "card")
        budget_box = QVBoxLayout(self.budget_card)
        budget_box.setSpacing(10)

        budget_title = QLabel("Anggaran Pengeluaran Bulan Ini")
        budget_title.setStyleSheet("font-weight: 600; font-size: 14px;")
        budget_box.addWidget(budget_title)

        self.budget_info_label = QLabel("Belum ada anggaran yang diatur.")
        self.budget_info_label.setProperty("class", "subtitle")
        budget_box.addWidget(self.budget_info_label)

        self.budget_progress = QProgressBar()
        self.budget_progress.setRange(0, 100)
        self.budget_progress.setValue(0)
        budget_box.addWidget(self.budget_progress)

        self.budget_detail_label = QLabel("")
        self.budget_detail_label.setStyleSheet("font-size: 12px; color: #A5A8B0;")
        budget_box.addWidget(self.budget_detail_label)

        middle_layout.addWidget(self.budget_card)

        # Survival Mode snapshot card
        self.survival_card = QFrame()
        self.survival_card.setProperty("class", "card")
        survival_box = QVBoxLayout(self.survival_card)
        survival_box.setSpacing(10)

        survival_title = QLabel("Student Survival Mode (Estimasi Belanja)")
        survival_title.setStyleSheet("font-weight: 600; font-size: 14px;")
        survival_box.addWidget(survival_title)

        self.survival_allowance_label = QLabel("Rp 0 / hari")
        self.survival_allowance_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #8B9BB4;")
        survival_box.addWidget(self.survival_allowance_label)

        self.survival_desc_label = QLabel("Estimasi batas aman pengeluaran harian.")
        self.survival_desc_label.setProperty("class", "subtitle")
        self.survival_desc_label.setWordWrap(True)
        survival_box.addWidget(self.survival_desc_label)

        middle_layout.addWidget(self.survival_card)

        main_layout.addLayout(middle_layout)

        # Recent transactions section
        recent_box = QVBoxLayout()
        recent_box.setSpacing(10)

        recent_header = QLabel("Transaksi Terbaru")
        recent_header.setStyleSheet("font-weight: 600; font-size: 14px;")
        recent_box.addWidget(recent_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tanggal", "Tipe", "Nominal", "Akun / Kategori", "Keterangan"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        recent_box.addWidget(self.table)
        main_layout.addLayout(recent_box)

    def update_user_name(self, name: Optional[str] = None) -> None:
        """Update dashboard greeting with user's name if set."""
        if name and name.strip():
            self.page_title.setText(f"Halo, {name.strip()}!")
            self.subtitle.setText("Pantau saldo dompet, arus kas bulanan, dan batas aman belanja harian Anda.")
        else:
            self.page_title.setText("Ikhtisar Keuangan Mahasiswa")
            self.subtitle.setText("Pantau saldo dompet, arus kas bulanan, dan batas aman belanja harian.")

    def refresh_data(self) -> None:
        """Fetch updated data from controller and refresh UI components."""
        user_name = self.controller.context.user_profile_repo.get_user_name()
        self.update_user_name(user_name)

        data = self.controller.get_dashboard_data()

        # Update metric cards
        self.card_total_balance.set_value(format_currency(data["total_balance"]))
        self.card_month_income.set_value(format_currency(data["month_income"]))
        self.card_month_expense.set_value(format_currency(data["month_expense"]))

        net = data["month_net"]
        net_str = format_currency(net)
        self.card_month_net.set_value(net_str)
        if net > 0:
            self.card_month_net.set_status("success")
        elif net < 0:
            self.card_month_net.set_status("danger")
        else:
            self.card_month_net.set_status("neutral")

        # Update Budget summary
        bs = data["budget_summary"]
        if bs["items_count"] > 0:
            pct = min(100, int(bs["percentage"]))
            self.budget_progress.setValue(pct)
            self.budget_info_label.setText(
                f"Terpakai {format_currency(bs['total_used'])} dari {format_currency(bs['total_budget'])} "
                f"({bs['percentage']}%)"
            )
            rem = bs["total_remaining"]
            if rem >= 0:
                self.budget_detail_label.setText(f"Sisa anggaran bulan ini: {format_currency(rem)}")
                self.budget_detail_label.setStyleSheet("color: #55B987; font-size: 12px;")
            else:
                self.budget_detail_label.setText(f"Melebihi anggaran sebesar: {format_currency(abs(rem))}")
                self.budget_detail_label.setStyleSheet("color: #E16D75; font-size: 12px;")
        else:
            self.budget_progress.setValue(0)
            self.budget_info_label.setText("Belum ada anggaran bulanan yang ditentukan.")
            self.budget_detail_label.setText("Silakan atur di menu Anggaran.")

        # Update Survival snapshot
        surv = data["survival_info"]
        self.survival_allowance_label.setText(f"{format_currency(surv.daily_allowance)} / hari")
        self.survival_desc_label.setText(surv.status_message)
        if surv.is_deficit:
            self.survival_allowance_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E16D75;")
        else:
            self.survival_allowance_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #55B987;")

        # Update Recent transactions table
        txns = data["recent_transactions"]
        self.table.setRowCount(len(txns))
        for row_idx, t in enumerate(txns):
            # Date
            item_date = QTableWidgetItem(format_date_display(t["date"], short=True))
            item_date.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, item_date)

            # Type
            type_label = "Pengeluaran"
            if t["type"] == "income":
                type_label = "Pemasukan"
            elif t["type"] == "transfer":
                type_label = "Transfer"
            item_type = QTableWidgetItem(type_label)
            item_type.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 1, item_type)

            # Amount
            item_amt = QTableWidgetItem(format_currency(t["amount"]))
            item_amt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if t["type"] == "income":
                item_amt.setForeground(Qt.GlobalColor.green)
            elif t["type"] == "expense":
                item_amt.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row_idx, 2, item_amt)

            # Account & Category
            if t["type"] == "transfer":
                detail_text = f"{t['account_name']} -> {t['to_account_name']}"
            else:
                detail_text = f"{t['account_name']} ({t['category_name']})"
            self.table.setItem(row_idx, 3, QTableWidgetItem(detail_text))

            # Description
            self.table.setItem(row_idx, 4, QTableWidgetItem(t["description"]))
