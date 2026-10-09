import ctypes
import logging
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.bootstrap import bootstrap_application
from app.config.settings import AppSettings
from app.views.main_window import MainWindow

logger = logging.getLogger("main")


def main() -> int:
    """Application main entry point."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("studentfinance.desktop.app.v1")
        except Exception:
            pass

    # Ensure high DPI scaling works cleanly
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("Student Finance")
    app.setOrganizationName("StudentFinance")

    # Set default system font
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    try:
        settings = AppSettings()
        context = bootstrap_application(settings)
    except Exception as e:
        logger.critical("Fatal error during application bootstrap: %s", e, exc_info=True)
        QMessageBox.critical(
            None,
            "Kesalahan Fatal Startup",
            f"Gagal memulai aplikasi:\n{e}\n\nPeriksa berkas log untuk rincian.",
        )
        return 1

    if context.settings.icon_path.exists():
        app.setWindowIcon(QIcon(str(context.settings.icon_path)))

    window = MainWindow(context)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
