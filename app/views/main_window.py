from __future__ import annotations

import logging
from datetime import date
from typing import List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.bootstrap import AppContext
from app.controllers.account_controller import AccountController
from app.controllers.budget_controller import BudgetController
from app.controllers.category_controller import CategoryController
from app.controllers.dashboard_controller import DashboardController
from app.controllers.report_controller import ReportController
from app.controllers.settings_controller import SettingsController
from app.controllers.survival_controller import SurvivalController
from app.controllers.transaction_controller import TransactionController
from app.ui.theme import QSS_STYLESHEET
from app.utils.formatters import format_date_display
from app.views.accounts_view import AccountsView
from app.views.budgets_view import BudgetsView
from app.views.categories_view import CategoriesView
from app.views.dashboard_view import DashboardView
from app.views.dialogs.about_dialog import AboutDialog
from app.views.dialogs.welcome_dialog import WelcomeDialog
from app.views.reports_view import ReportsView
from app.views.settings_view import SettingsView
from app.views.survival_view import SurvivalView
from app.views.transactions_view import TransactionsView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation and stacked view pages."""

    def __init__(self, context: AppContext):
        super().__init__()
        self.context = context
        self.setWindowTitle(context.settings.app_name)
        self.resize(1200, 800)
        self.setMinimumSize(1000, 650)

        # Apply application icon
        if context.settings.icon_path.exists():
            self.setWindowIcon(QIcon(str(context.settings.icon_path)))

        # Apply global stylesheet
        self.setStyleSheet(QSS_STYLESHEET)

        # Initialize Controllers
        self.dashboard_ctrl = DashboardController(self.context)
        self.transaction_ctrl = TransactionController(self.context)
        self.account_ctrl = AccountController(self.context)
        self.category_ctrl = CategoryController(self.context)
        self.budget_ctrl = BudgetController(self.context)
        self.report_ctrl = ReportController(self.context)
        self.survival_ctrl = SurvivalController(self.context)
        self.settings_ctrl = SettingsController(self.context)

        self.init_ui()
        self.setup_shortcuts()

        # Update user greeting from database
        self.update_user_greeting()

        # Show first page
        self.nav_buttons[0].setChecked(True)
        self.switch_page(0)

        # Check for first-time onboarding (when user name is empty in database)
        QTimer.singleShot(200, self.check_initial_setup)

    def init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = self._create_sidebar()
        root_layout.addWidget(sidebar)

        # 2. Right Content Area
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Header
        top_header = self._create_top_header()
        content_layout.addWidget(top_header)

        # Stacked pages
        self.stack = QStackedWidget()

        # Build Views
        self.dashboard_view = DashboardView(self.dashboard_ctrl, on_record_transaction=self._quick_add_transaction)
        self.transactions_view = TransactionsView(self.transaction_ctrl, on_data_changed=self.on_global_data_changed)
        self.accounts_view = AccountsView(self.account_ctrl, on_data_changed=self.on_global_data_changed)
        self.categories_view = CategoriesView(self.category_ctrl, on_data_changed=self.on_global_data_changed)
        self.budgets_view = BudgetsView(self.budget_ctrl, on_data_changed=self.on_global_data_changed)
        self.reports_view = ReportsView(self.report_ctrl)
        self.survival_view = SurvivalView(self.survival_ctrl)
        self.settings_view = SettingsView(
            self.settings_ctrl,
            on_data_restored=self.on_global_data_changed,
            on_user_name_changed=self.on_user_name_updated,
        )

        self.views: List[QWidget] = [
            self.dashboard_view,
            self.transactions_view,
            self.accounts_view,
            self.categories_view,
            self.budgets_view,
            self.reports_view,
            self.survival_view,
            self.settings_view,
        ]

        for v in self.views:
            # Wrap in scroll area so small screens (e.g. 1366x768) don't clip
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setWidget(v)
            self.stack.addWidget(scroll)

        content_layout.addWidget(self.stack)
        root_layout.addWidget(content_container, 1)

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("SidebarWidget")
        sidebar.setFixedWidth(230)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 20)
        layout.setSpacing(8)

        # App brand title with icon
        brand_container = QHBoxLayout()
        brand_container.setSpacing(10)
        brand_container.setContentsMargins(0, 0, 0, 8)

        if self.context.settings.icon_path.exists():
            icon_lbl = QLabel()
            pixmap = QPixmap(str(self.context.settings.icon_path)).scaled(
                36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_lbl.setPixmap(pixmap)
            brand_container.addWidget(icon_lbl)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(2)
        brand_title = QLabel("STUDENT FINANCE")
        brand_title.setObjectName("SidebarTitle")
        brand_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; letter-spacing: 0.5px; color: #F2F3F5; padding: 0;"
        )
        sub_title = QLabel("Aplikasi Keuangan Mahasiswa")
        sub_title.setStyleSheet("font-size: 11px; color: #8B9BB4; padding: 0;")
        brand_box.addWidget(brand_title)
        brand_box.addWidget(sub_title)
        brand_container.addLayout(brand_box)
        layout.addLayout(brand_container)

        # Navigation buttons
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        nav_items = [
            "Dashboard",
            "Transaksi",
            "Akun & Dompet",
            "Kategori",
            "Anggaran",
            "Laporan Keuangan",
            "Survival Mode",
            "Pengaturan & Backup",
        ]

        self.nav_buttons: List[QPushButton] = []
        for idx, text in enumerate(nav_items):
            # Escape ampersands so QPushButton doesn't treat them as mnemonic accelerator keys
            btn = QPushButton(text.replace("&", "&&"))
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            self.btn_group.addButton(btn, idx)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        self.btn_group.idClicked.connect(self.switch_page)

        layout.addStretch()

        # Footer About button
        btn_about = QPushButton("Tentang Aplikasi")
        btn_about.setObjectName("AboutSidebarButton")
        btn_about.setCursor(Qt.PointingHandCursor)
        btn_about.setStyleSheet(
            "QPushButton { background-color: #202228; border: 1px solid #333640; border-radius: 4px; "
            "color: #8B9BB4; font-size: 11px; padding: 6px; } "
            "QPushButton:hover { background-color: #282B33; color: #F2F3F5; border-color: #4B5563; }"
        )
        btn_about.clicked.connect(self.show_about_dialog)
        layout.addWidget(btn_about)

        return sidebar

    def _create_top_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("HeaderWidget")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)

        self.header_page_title = QLabel("Dashboard")
        self.header_page_title.setObjectName("HeaderTitle")
        layout.addWidget(self.header_page_title)

        layout.addStretch()

        # User greeting display
        self.user_greeting_lbl = QLabel("")
        self.user_greeting_lbl.setStyleSheet("font-size: 12px; color: #8B9BB4; font-weight: 500; margin-right: 14px;")
        layout.addWidget(self.user_greeting_lbl)

        # Current date display
        today_str = format_date_display(date.today())
        date_lbl = QLabel(today_str)
        date_lbl.setStyleSheet("font-size: 12px; color: #A5A8B0; font-weight: 500; margin-right: 14px;")
        layout.addWidget(date_lbl)

        # About button in header
        btn_header_about = QPushButton("Tentang")
        btn_header_about.setCursor(Qt.PointingHandCursor)
        btn_header_about.setStyleSheet(
            "QPushButton { font-size: 11px; padding: 4px 10px; background-color: #202228; "
            "border: 1px solid #333640; border-radius: 4px; color: #8B9BB4; } "
            "QPushButton:hover { background-color: #282B33; color: #F2F3F5; border-color: #4B5563; }"
        )
        btn_header_about.clicked.connect(self.show_about_dialog)
        layout.addWidget(btn_header_about)

        return header

    def setup_shortcuts(self) -> None:
        """Configure keyboard navigation shortcuts."""
        # Quick new transaction: Ctrl+N
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._quick_add_transaction)

        # Refresh active view: F5
        QShortcut(QKeySequence("F5"), self, activated=self.refresh_active_view)

        # Switching pages: Ctrl+1 to Ctrl+8
        for i in range(len(self.views)):
            shortcut_key = f"Ctrl+{i + 1}"
            QShortcut(QKeySequence(shortcut_key), self, activated=lambda idx=i: self._select_page(idx))

    def _select_page(self, index: int) -> None:
        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)
            self.switch_page(index)

    def switch_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        page_titles = [
            "Dashboard",
            "Transaksi",
            "Akun & Dompet",
            "Kategori",
            "Anggaran",
            "Laporan Keuangan",
            "Survival Mode",
            "Pengaturan & Backup",
        ]
        if 0 <= index < len(page_titles):
            self.header_page_title.setText(page_titles[index])

        # Refresh data on view switch
        self.refresh_active_view()

    def refresh_active_view(self) -> None:
        idx = self.stack.currentIndex()
        if 0 <= idx < len(self.views):
            active_widget = self.views[idx]
            if hasattr(active_widget, "refresh_data"):
                active_widget.refresh_data()

    def on_global_data_changed(self) -> None:
        """Triggered when any transaction, account, category, or budget is created/updated/deleted."""
        self.refresh_active_view()

    def _quick_add_transaction(self) -> None:
        """Quickly opens add transaction dialog from anywhere."""
        self.transactions_view._open_add_dialog()

    def update_user_greeting(self) -> None:
        """Update top header and dashboard greetings from database."""
        name = self.settings_ctrl.get_user_name()
        if name:
            self.user_greeting_lbl.setText(f"Pengguna: {name}")
            self.dashboard_view.update_user_name(name)
        else:
            self.user_greeting_lbl.setText("")
            self.dashboard_view.update_user_name(None)

    def on_user_name_updated(self, name: str) -> None:
        """Callback invoked when user updates their name in Settings or onboarding."""
        self.update_user_greeting()

    def check_initial_setup(self) -> None:
        """Prompt for user name upon first application launch if not set in database."""
        name = self.settings_ctrl.get_user_name()
        if not name:
            dlg = WelcomeDialog(icon_path=self.context.settings.icon_path, parent=self)
            if dlg.exec():
                new_name = dlg.get_name()
                if new_name:
                    self.settings_ctrl.update_user_name(new_name)
                    self.on_user_name_updated(new_name)

    def show_about_dialog(self) -> None:
        """Open modal dialog showing version and developer details."""
        dlg = AboutDialog(self.context.settings, parent=self)
        dlg.exec()
