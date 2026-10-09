from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from app.bootstrap import AppContext
from app.controllers.settings_controller import SettingsController
from app.views.dialogs.about_dialog import AboutDialog
from app.views.dialogs.welcome_dialog import WelcomeDialog


def test_settings_controller_profile_and_info(app_context: AppContext):
    ctrl = SettingsController(app_context)

    # Initial name is None
    assert ctrl.get_user_name() is None

    # Update name
    name = ctrl.update_user_name("Alfando")
    assert name == "Alfando"
    assert ctrl.get_user_name() == "Alfando"

    # System info checks
    info = ctrl.get_system_info()
    assert info["app_name"] == "Student Finance"
    assert info["version"] == "0.1.0"
    assert info["developer_name"] == "AlfandoXeon"
    assert info["developer_website"] == "https://alfandoxeon.freedev.app"


def test_about_dialog(app_context: AppContext, qtbot):
    dlg = AboutDialog(app_context.settings)
    qtbot.addWidget(dlg)

    assert dlg.windowTitle() == "Tentang Student Finance"
    labels = [lbl.text() for lbl in dlg.findChildren(QLabel)]
    assert any(app_context.settings.developer_name in t for t in labels)
    assert any(app_context.settings.developer_website in t for t in labels)
    assert dlg.close_btn.isDefault()


def test_welcome_dialog(qtbot):
    dlg = WelcomeDialog()
    qtbot.addWidget(dlg)

    assert dlg.windowTitle() == "Selamat Datang di Student Finance"
    assert dlg.submit_btn.isDefault()

    # Empty submit rejected
    dlg.name_input.setText("   ")
    qtbot.mouseClick(dlg.submit_btn, Qt.LeftButton)
    assert dlg.error_label.text() != ""
    assert dlg.get_name() == ""

    # Valid name accepted
    dlg.name_input.setText("Alfando")
    qtbot.mouseClick(dlg.submit_btn, Qt.LeftButton)
    assert dlg.get_name() == "Alfando"
