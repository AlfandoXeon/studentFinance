from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.database.database_manager import DatabaseManager
from app.utils.validators import ValidationError

logger = logging.getLogger(__name__)


class BackupService:
    """Service to create, validate, and restore SQLite database backups."""

    def __init__(self, db_manager: DatabaseManager, backup_dir: Path):
        self.db_manager = db_manager
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, custom_filename: Optional[str] = None) -> Path:
        """Create a consistent backup of the current database using SQLite's backup API."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = custom_filename or f"backup_finance_{timestamp}.db"
        dest_path = self.backup_dir / filename

        self.db_manager.backup_database(dest_path)
        logger.info("Backup created at %s", dest_path)
        return dest_path

    def validate_backup_file(self, backup_file_path: Path) -> bool:
        """Verify that the backup file is a valid, readable SQLite database

        with the expected schema tables.
        """
        path = Path(backup_file_path)
        if not path.is_file():
            raise ValidationError(f"File backup tidak ditemukan: {path}")

        if path.stat().st_size == 0:
            raise ValidationError("File backup kosong (0 bytes).")

        try:
            conn = sqlite3.connect(str(path))
            cursor = conn.cursor()

            # Integrity check
            cursor.execute("PRAGMA quick_check;")
            result = cursor.fetchone()
            if not result or result[0] != "ok":
                raise ValidationError(f"Integritas database cadangan rusak: {result}")

            # Check required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}
            required_tables = {"accounts", "categories", "transactions", "budgets"}
            missing = required_tables - tables
            if missing:
                raise ValidationError(f"File cadangan tidak memiliki tabel yang diperlukan: {missing}")

            conn.close()
            return True
        except sqlite3.Error as e:
            raise ValidationError(f"Format file cadangan SQLite tidak valid: {e}") from e

    def restore_backup(self, backup_file_path: Path) -> Path:
        """Safely restore database from backup.

        1. Validates the backup file.
        2. Creates an automatic recovery snapshot of current data before replacement.
        3. Restores backup file into live database.
        """
        self.validate_backup_file(backup_file_path)

        # 1. Create recovery snapshot of live db first
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery_path = self.backup_dir / f"recovery_pre_restore_{timestamp}.db"
        try:
            self.db_manager.backup_database(recovery_path)
            logger.info("Created pre-restore recovery snapshot at %s", recovery_path)
        except Exception as e:
            logger.warning("Could not create pre-restore snapshot (database might be new): %s", e)

        # 2. Restore into target database using backup API
        src_conn = sqlite3.connect(str(backup_file_path))
        dest_conn = self.db_manager.get_connection()
        try:
            with dest_conn:
                src_conn.backup(dest_conn)
            logger.info("Database successfully restored from %s", backup_file_path)
        finally:
            src_conn.close()
            dest_conn.close()

        return recovery_path

    def list_backups(self) -> List[Path]:
        """List all available backup files sorted by modification time descending."""
        if not self.backup_dir.exists():
            return []
        files = [f for f in self.backup_dir.glob("*.db") if f.is_file()]
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return files
