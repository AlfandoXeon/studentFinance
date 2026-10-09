from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.controllers.survival_controller import SurvivalController
from app.ui.components.currency_line_edit import CurrencyLineEdit
from app.utils.formatters import format_currency, parse_currency


class SurvivalView(QWidget):
    """View for Student Survival Mode: daily spending limits and budget survival calculator."""

    def __init__(self, controller: SurvivalController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(20)

        # Header
        title_box = QVBoxLayout()
        title = QLabel("Student Survival Mode")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #F2F3F5;")
        subtitle = QLabel("Hitung batas aman belanja harian Anda hingga jadwal penerimaan uang saku berikutnya.")
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        main_layout.addLayout(title_box)

        # Content horizontal split
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left: Input Form Card
        input_card = QFrame()
        input_card.setProperty("class", "card")
        form_box = QVBoxLayout(input_card)
        form_box.setSpacing(16)

        card_title = QLabel("Parameter Perhitungan")
        card_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #F2F3F5;")
        form_box.addWidget(card_title)

        form = QFormLayout()
        form.setSpacing(12)

        # Current total balance
        self.balance_label = QLabel("Rp 0")
        self.balance_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #55B987;")
        form.addRow("Total Saldo Tersedia:", self.balance_label)

        # Next income date
        self.income_date_input = QDateEdit()
        self.income_date_input.setCalendarPopup(True)
        self.income_date_input.setDisplayFormat("yyyy-MM-dd")
        self.income_date_input.setDate(QDate.currentDate().addDays(7))
        form.addRow("Target Pemasukan Berikutnya:", self.income_date_input)

        # Planned mandatory expenses with live thousands separator
        self.mandatory_input = CurrencyLineEdit()
        self.mandatory_input.setPlaceholderText("Misal: 150,000 (uang kos, tagihan, dll)")
        self.mandatory_input.setText("0")
        self.mandatory_input.returnPressed.connect(self._calculate)
        form.addRow("Rencana Pengeluaran Wajib (Rp):", self.mandatory_input)

        form_box.addLayout(form)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E16D75; font-size: 12px;")
        form_box.addWidget(self.error_label)

        self.calc_btn = QPushButton("Hitung Estimasi Belanja Aman")
        self.calc_btn.setProperty("class", "primary-btn")
        self.calc_btn.setDefault(True)
        self.calc_btn.clicked.connect(self._calculate)
        form_box.addWidget(self.calc_btn)

        content_layout.addWidget(input_card, 1)

        # Right: Output Results Card
        self.result_card = QFrame()
        self.result_card.setProperty("class", "card")
        result_box = QVBoxLayout(self.result_card)
        result_box.setSpacing(16)

        res_title = QLabel("Rekomendasi Alokasi Harian")
        res_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #F2F3F5;")
        result_box.addWidget(res_title)

        # Daily spending limit
        self.daily_limit_lbl = QLabel("Rp 0")
        self.daily_limit_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: #8B9BB4;")
        result_box.addWidget(self.daily_limit_lbl)

        self.daily_sub_lbl = QLabel("Batas belanja aman per hari")
        self.daily_sub_lbl.setProperty("class", "subtitle")
        result_box.addWidget(self.daily_sub_lbl)

        # Metrics details
        self.days_lbl = QLabel("Sisa Waktu: 0 hari")
        self.days_lbl.setStyleSheet("font-size: 13px; color: #F2F3F5;")
        result_box.addWidget(self.days_lbl)

        self.discretionary_lbl = QLabel("Saldo Bebas Tersedia: Rp 0")
        self.discretionary_lbl.setStyleSheet("font-size: 13px; color: #F2F3F5;")
        result_box.addWidget(self.discretionary_lbl)

        self.status_box = QLabel("")
        self.status_box.setWordWrap(True)
        self.status_box.setStyleSheet(
            "padding: 10px; background-color: #202125; border-radius: 6px; font-size: 12px; color: #A5A8B0;"
        )
        result_box.addWidget(self.status_box)

        # Disclaimer
        disclaimer = QLabel(
            "Catatan: Perhitungan ini merupakan estimasi rekomendasi dan tidak memotong saldo akun secara otomatis."
        )
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet("font-size: 11px; color: #737682; font-style: italic;")
        result_box.addWidget(disclaimer)

        result_box.addStretch()
        content_layout.addWidget(self.result_card, 1)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

    def refresh_data(self) -> None:
        """Fetch total balance and recalculate."""
        cur_bal = self.controller.get_current_balance()
        self.balance_label.setText(format_currency(cur_bal))
        self._calculate()

    def _calculate(self) -> None:
        self.error_label.setText("")
        target_date_str = self.income_date_input.date().toString("yyyy-MM-dd")

        text_mandatory = self.mandatory_input.text().strip()
        if not text_mandatory or text_mandatory == "0":
            mandatory_amount = 0
        else:
            try:
                mandatory_amount = parse_currency(text_mandatory)
            except ValueError as e:
                self.error_label.setText(str(e))
                return

        estimate = self.controller.calculate_survival(
            expected_income_date=target_date_str,
            planned_mandatory_expenses=mandatory_amount,
        )

        self.daily_limit_lbl.setText(format_currency(estimate.daily_allowance))
        self.days_lbl.setText(f"Sisa Waktu: {estimate.days_remaining} hari (sampai {estimate.target_date})")
        self.discretionary_lbl.setText(f"Saldo Bebas Tersedia: {format_currency(estimate.available_discretionary)}")
        self.status_box.setText(estimate.status_message)

        if estimate.is_deficit:
            self.daily_limit_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: #E16D75;")
            self.status_box.setStyleSheet(
                "padding: 10px; background-color: #381C1E; "
                "border: 1px solid #7E3B40; border-radius: 6px; font-size: 12px; color: #F8B4B8;"
            )
        else:
            self.daily_limit_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: #55B987;")
            self.status_box.setStyleSheet(
                "padding: 10px; background-color: #192D23; "
                "border: 1px solid #2B6248; border-radius: 6px; font-size: 12px; color: #B4E6CC;"
            )
