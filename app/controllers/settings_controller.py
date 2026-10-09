from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.bootstrap import AppContext


class SettingsController:
    """Controller for backups, restore, and system configuration."""

    def __init__(self, context: AppContext):
        self.context = context

    def get_user_name(self) -> Optional[str]:
        """Get current user's configured name, or None if not set."""
        return self.context.user_profile_repo.get_user_name()

    def update_user_name(self, name: str) -> str:
        """Update and persist the user's name."""
        return self.context.user_profile_repo.set_user_name(name)

    def get_system_info(self) -> Dict[str, Any]:
        """Get application and environment specifications."""
        return {
            "app_name": self.context.settings.app_name,
            "version": self.context.settings.version,
            "developer_name": self.context.settings.developer_name,
            "developer_website": self.context.settings.developer_website,
            "currency": f"{self.context.settings.currency_symbol} ({self.context.settings.currency_code})",
            "db_path": str(self.context.settings.db_path),
            "backup_dir": str(self.context.settings.backup_dir),
            "logs_dir": str(self.context.settings.logs_dir),
            "storage_engine": "SQLite 3 with WAL Mode",
        }

    def create_backup(self) -> Path:
        return self.context.backup_service.create_backup()

    def list_backups(self) -> List[Path]:
        return self.context.backup_service.list_backups()

    def restore_backup(self, backup_path: Path) -> Path:
        return self.context.backup_service.restore_backup(backup_path)
