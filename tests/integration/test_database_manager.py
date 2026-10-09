from __future__ import annotations

from pathlib import Path

from app.database.database_manager import DatabaseManager
from app.database.schema import CURRENT_SCHEMA_VERSION


def test_database_manager_initialization(tmp_path: Path):
    db_file = tmp_path / "test.db"
    mgr = DatabaseManager(db_file)

    mgr.initialize_database()
    assert db_file.exists()
    assert mgr.get_schema_version() == CURRENT_SCHEMA_VERSION

    # Idempotent: run again without errors or data duplication
    mgr.initialize_database()
    assert mgr.get_schema_version() == CURRENT_SCHEMA_VERSION

    with mgr.get_connection() as conn:
        cursor = conn.execute("PRAGMA foreign_keys;")
        assert cursor.fetchone()[0] == 1

        cursor = conn.execute("SELECT COUNT(*) FROM categories;")
        count = cursor.fetchone()[0]
        assert count > 0

        cursor = conn.execute("SELECT COUNT(*) FROM accounts;")
        acc_count = cursor.fetchone()[0]
        assert acc_count > 0

        cursor = conn.execute("SELECT COUNT(*) FROM user_profile;")
        user_count = cursor.fetchone()[0]
        assert user_count == 1
