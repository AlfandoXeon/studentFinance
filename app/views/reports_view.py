from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.controllers.report_controller import ReportController
from app.utils.formatters import format_currency


class ReportsView(QWidget):
    """View for financial reports, category expense distribution, and data exports."""

    def __init__(self, controller: ReportController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Laporan & Analisis Keuangan")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Evaluasi perputaran dana, distribusi pengeluaran, dan tren keuangan.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.export_btn = QPushButton("Unduh Laporan CSV")
        self.export_btn.clicked.connect(self._export_csv)
        header_layout.addWidget(self.export_btn)

        main_layout.addLayout(header_layout)

        # Period Filter Bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        filter_layout.addWidget(QLabel("Periode:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Bulan Ini", "this_month")
        self.preset_combo.addItem("7 Hari Terakhir", "last_7")
        self.preset_combo.addItem("30 Hari Terakhir", "last_30")
        self.preset_combo.addItem("Tahun Ini", "this_year")
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        filter_layout.addWidget(self.preset_combo)

        filter_layout.addWidget(QLabel("Dari:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.dateChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("Sampai:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.dateChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.date_to)

        filter_layout.addStretch()

        main_layout.addLayout(filter_layout)

        # Metrics cards row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)

        self.card_inc = self._create_card("Total Pemasukan", "Rp 0", "#55B987")
        self.card_exp = self._create_card("Total Pengeluaran", "Rp 0", "#E16D75")
        self.card_net = self._create_card("Arus Kas Bersih", "Rp 0", "#8B9BB4")
        self.card_avg = self._create_card("Rata-rata Pengeluaran / Hari", "Rp 0", "#F2F3F5")

        metrics_layout.addWidget(self.card_inc)
        metrics_layout.addWidget(self.card_exp)
        metrics_layout.addWidget(self.card_net)
        metrics_layout.addWidget(self.card_avg)

        main_layout.addLayout(metrics_layout)

        # Category spending breakdown
        section_label = QLabel("Distribusi Pengeluaran Berdasarkan Kategori")
        section_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        main_layout.addWidget(section_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            [
                "Kategori Pengeluaran",
                "Total Pengeluaran",
                "Porsi / Persentase",
                "Jumlah Transaksi",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table)

        # Initialize to this month
        self._on_preset_changed()

    def _create_card(self, title: str, val: str, color: str) -> QFrame:
        card = QFrame()
        card.setProperty("class", "card")
        box = QVBoxLayout(card)
        box.setSpacing(8)

        t_lbl = QLabel(title)
        t_lbl.setProperty("class", "subtitle")
        box.addWidget(t_lbl)

        v_lbl = QLabel(val)
        v_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        v_lbl.setObjectName("card_value")
        box.addWidget(v_lbl)

        return card

    def _on_preset_changed(self) -> None:
        today = date.today()
        preset = self.preset_combo.currentData()

        self.date_from.blockSignals(True)
        self.date_to.blockSignals(True)

        if preset == "this_month":
            d_start = today.replace(day=1)
            d_end = today
        elif preset == "last_7":
            d_start = today.fromordinal(today.toordinal() - 6)
            d_end = today
        elif preset == "last_30":
            d_start = today.fromordinal(today.toordinal() - 29)
            d_end = today
        elif preset == "this_year":
            d_start = today.replace(month=1, day=1)
            d_end = today
        else:
            d_start = today.replace(day=1)
            d_end = today

        self.date_from.setDate(QDate(d_start.year, d_start.month, d_start.day))
        self.date_to.setDate(QDate(d_end.year, d_end.month, d_end.day))

        self.date_from.blockSignals(False)
        self.date_to.blockSignals(False)

        self.refresh_data()

    def refresh_data(self) -> None:
        """Fetch report from controller and update UI."""
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")

        if start_date > end_date:
            return

        report = self.controller.generate_report(start_date, end_date)

        # Update cards
        self.card_inc.findChild(QLabel, "card_value").setText(format_currency(report.total_income))
        self.card_exp.findChild(QLabel, "card_value").setText(format_currency(report.total_expense))

        net_val_lbl = self.card_net.findChild(QLabel, "card_value")
        net_val_lbl.setText(format_currency(report.net_cashflow))
        if report.net_cashflow > 0:
            net_val_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #55B987;")
        elif report.net_cashflow < 0:
            net_val_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #E16D75;")
        else:
            net_val_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #8B9BB4;")

        self.card_avg.findChild(QLabel, "card_value").setText(format_currency(report.average_daily_expense))

        # Update table
        self.table.setRowCount(len(report.category_spendings))
        for row_idx, item in enumerate(report.category_spendings):
            # Category
            self.table.setItem(row_idx, 0, QTableWidgetItem(item.category_name))

            # Total
            item_tot = QTableWidgetItem(format_currency(item.total_amount))
            item_tot.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 1, item_tot)

            # Percentage
            item_pct = QTableWidgetItem(f"{item.percentage:.1f}%")
            item_pct.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 2, item_pct)

            # Txn count
            item_cnt = QTableWidgetItem(f"{item.transaction_count} kali")
            item_cnt.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 3, item_cnt)

    def _export_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Simpan Laporan CSV", "laporan_keuangan.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            start_date = self.date_from.date().toString("yyyy-MM-dd")
            end_date = self.date_to.date().toString("yyyy-MM-dd")
            csv_text = self.controller.export_csv(start_date, end_date)
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_text)
            QMessageBox.information(self, "Berhasil", f"Laporan transaksi berhasil disimpan ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Gagal Ekspor", str(e))
