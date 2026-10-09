from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    """Color palette tokens for professional dark grey theme."""

    MAIN_BG: str = "#18191C"
    SIDEBAR_BG: str = "#202125"
    CARD_BG: str = "#26282D"
    ELEVATED_SURFACE: str = "#2E3036"
    PRIMARY_TEXT: str = "#F2F3F5"
    SECONDARY_TEXT: str = "#A5A8B0"
    BORDER: str = "#3A3D44"
    PRIMARY_ACCENT: str = "#8B9BB4"
    ACCENT_HOVER: str = "#9EADC5"
    SUCCESS: str = "#55B987"
    WARNING: str = "#E6B566"
    ERROR: str = "#E16D75"


COLORS = ThemeColors()

QSS_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {COLORS.MAIN_BG};
    color: {COLORS.PRIMARY_TEXT};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}}

QWidget {{
    color: {COLORS.PRIMARY_TEXT};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}}

/* Sidebar */
#SidebarWidget {{
    background-color: {COLORS.SIDEBAR_BG};
    border-right: 1px solid {COLORS.BORDER};
}}

#SidebarTitle {{
    font-size: 16px;
    font-weight: bold;
    color: {COLORS.PRIMARY_TEXT};
    padding: 16px 12px;
}}

#NavButton {{
    background-color: transparent;
    color: {COLORS.SECONDARY_TEXT};
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
}}

#NavButton:hover {{
    background-color: {COLORS.CARD_BG};
    color: {COLORS.PRIMARY_TEXT};
}}

#NavButton:checked {{
    background-color: {COLORS.ELEVATED_SURFACE};
    color: {COLORS.PRIMARY_TEXT};
    font-weight: bold;
    border-left: 3px solid {COLORS.PRIMARY_ACCENT};
}}

/* Header */
#HeaderWidget {{
    background-color: {COLORS.SIDEBAR_BG};
    border-bottom: 1px solid {COLORS.BORDER};
    padding: 10px 20px;
}}

#HeaderTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS.PRIMARY_TEXT};
}}

/* Cards */
QFrame.card {{
    background-color: {COLORS.CARD_BG};
    border: 1px solid {COLORS.BORDER};
    border-radius: 8px;
    padding: 16px;
}}

QFrame.card:hover {{
    border: 1px solid {COLORS.PRIMARY_ACCENT};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS.ELEVATED_SURFACE};
    color: {COLORS.PRIMARY_TEXT};
    border: 1px solid {COLORS.BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS.BORDER};
    border-color: {COLORS.PRIMARY_ACCENT};
}}

QPushButton:pressed {{
    background-color: {COLORS.CARD_BG};
}}

QPushButton:disabled {{
    background-color: {COLORS.CARD_BG};
    color: #63666E;
    border-color: {COLORS.CARD_BG};
}}

QPushButton.primary-btn {{
    background-color: #3B4B61;
    color: #FFFFFF;
    border: 1px solid #5A6F8F;
    font-weight: 600;
}}

QPushButton.primary-btn:hover {{
    background-color: #485C77;
}}

QPushButton.danger-btn {{
    background-color: #52272B;
    color: #F8B4B8;
    border: 1px solid #7E3B40;
}}

QPushButton.danger-btn:hover {{
    background-color: #693237;
}}

/* Input controls */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {{
    background-color: {COLORS.ELEVATED_SURFACE};
    color: {COLORS.PRIMARY_TEXT};
    border: 1px solid {COLORS.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {COLORS.PRIMARY_ACCENT};
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {COLORS.PRIMARY_ACCENT};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: none;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS.ELEVATED_SURFACE};
    color: {COLORS.PRIMARY_TEXT};
    selection-background-color: {COLORS.CARD_BG};
    border: 1px solid {COLORS.BORDER};
}}

/* Tables */
QTableWidget, QTableView {{
    background-color: {COLORS.CARD_BG};
    color: {COLORS.PRIMARY_TEXT};
    border: 1px solid {COLORS.BORDER};
    border-radius: 6px;
    gridline-color: {COLORS.BORDER};
    selection-background-color: {COLORS.ELEVATED_SURFACE};
    selection-color: {COLORS.PRIMARY_TEXT};
}}

QHeaderView::section {{
    background-color: {COLORS.SIDEBAR_BG};
    color: {COLORS.SECONDARY_TEXT};
    border: none;
    border-bottom: 1px solid {COLORS.BORDER};
    padding: 8px 10px;
    font-weight: 600;
    text-align: left;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {COLORS.MAIN_BG};
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS.BORDER};
    min-height: 20px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS.PRIMARY_ACCENT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Labels */
QLabel.subtitle {{
    color: {COLORS.SECONDARY_TEXT};
    font-size: 12px;
}}

QLabel.metric-value {{
    font-size: 22px;
    font-weight: bold;
    color: {COLORS.PRIMARY_TEXT};
}}

QLabel.metric-success {{
    color: {COLORS.SUCCESS};
}}

QLabel.metric-danger {{
    color: {COLORS.ERROR};
}}

QLabel.metric-warning {{
    color: {COLORS.WARNING};
}}

/* Progress bars */
QProgressBar {{
    border: 1px solid {COLORS.BORDER};
    border-radius: 4px;
    text-align: center;
    background-color: {COLORS.ELEVATED_SURFACE};
    color: {COLORS.PRIMARY_TEXT};
    font-size: 11px;
    height: 14px;
}}

QProgressBar::chunk {{
    background-color: {COLORS.PRIMARY_ACCENT};
    border-radius: 3px;
}}
"""
