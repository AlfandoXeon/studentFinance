from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

from app.database.database_manager import DatabaseManager
from app.models.user_profile import UserProfile


class UserProfileRepository:
    """Repository for accessing and updating user profile settings."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _row_to_model(self, row: sqlite3.Row) -> UserProfile:
        return UserProfile(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_profile(self, conn: Optional[sqlite3.Connection] = None) -> Optional[UserProfile]:
        """Fetch the single user profile row."""
        query = "SELECT * FROM user_profile WHERE id = 1;"
        if conn is not None:
            cursor = conn.execute(query)
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query)
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_user_name(self, conn: Optional[sqlite3.Connection] = None) -> Optional[str]:
        """Fetch the user's name if set, or None if empty."""
        profile = self.get_profile(conn=conn)
        if profile and profile.name and profile.name.strip():
            return profile.name.strip()
        return None

    def set_user_name(self, name: str, conn: Optional[sqlite3.Connection] = None) -> str:
        """Update or insert the user's name."""
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Nama pengguna tidak boleh kosong.")

        now = datetime.now().isoformat()
        query = """
            INSERT INTO user_profile (id, name, created_at, updated_at)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                updated_at = excluded.updated_at;
        """
        params = (cleaned_name, now, now)

        if conn is not None:
            conn.execute(query, params)
            return cleaned_name

        with self.db_manager.transaction() as c:
            c.execute(query, params)
            return cleaned_name
