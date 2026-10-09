from __future__ import annotations

import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Return the root directory of the project reliably, whether running from source or frozen."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller executable
        return Path(sys.executable).resolve().parent
    # app/config/paths.py -> app/config -> app -> project root
    return Path(__file__).resolve().parent.parent.parent


def get_default_database_path() -> Path:
    """Resolve the database path relative to project root during development,

    or in user app data if explicitly configured / packaged without local write access.
    """
    root = get_project_root()
    # In development mode, finance.db in the project root
    dev_db = root / "finance.db"

    # If portable / dev root is writable, use project root
    try:
        # Check if root is writable
        test_file = root / ".write_test"
        test_file.touch(exist_ok=True)
        test_file.unlink(missing_ok=True)
        return dev_db
    except (OSError, PermissionError):
        # Fallback to APPDATA / local app data on Windows or ~/.local/share on Linux
        app_data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "StudentFinance"
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return app_data_dir / "finance.db"


def get_backup_dir() -> Path:
    """Return directory for local database backups."""
    root = get_project_root()
    backup_dir = root / "backups"
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    except (OSError, PermissionError):
        app_data_dir = (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "StudentFinance" / "backups"
        )
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return app_data_dir


def get_logs_dir() -> Path:
    """Return directory for application logs."""
    root = get_project_root()
    log_dir = root / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    except (OSError, PermissionError):
        app_data_dir = (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "StudentFinance" / "logs"
        )
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return app_data_dir


def get_app_icon_path() -> Path:
    """Return path to application icon file (png), checking bundle and root locations."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            bundled_icon = Path(meipass) / "icon" / "icon.png"
            if bundled_icon.exists():
                return bundled_icon
        exe_icon = Path(sys.executable).resolve().parent / "icon" / "icon.png"
        if exe_icon.exists():
            return exe_icon
    return get_project_root() / "icon" / "icon.png"
