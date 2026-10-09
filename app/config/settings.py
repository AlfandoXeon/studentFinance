from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config.paths import get_app_icon_path, get_backup_dir, get_default_database_path, get_logs_dir


@dataclass
class AppSettings:
    """Application configuration settings."""

    app_name: str = "Student Finance"
    version: str = "0.1.0"
    developer_name: str = "AlfandoXeon"
    developer_website: str = "https://alfandoxeon.freedev.app"
    currency_code: str = "IDR"
    currency_symbol: str = "Rp"
    db_path: Path = field(default_factory=get_default_database_path)
    icon_path: Path = field(default_factory=get_app_icon_path)
    backup_dir: Path = field(default_factory=get_backup_dir)
    logs_dir: Path = field(default_factory=get_logs_dir)
    budget_warning_threshold: float = 0.80  # 80% threshold for warnings
    log_level: str = "INFO"
