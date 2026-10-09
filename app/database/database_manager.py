from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from app.database.schema import DEFAULT_CATEGORIES, SCHEMA_V1_STATEMENTS, SCHEMA_V2_STATEMENTS

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite connections, migrations, and transactions."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a new SQLite connection."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        # Always enforce foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")
        # WAL mode for performance and concurrent read safety
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    @contextmanager
    def transaction(self, conn: Optional[sqlite3.Connection] = None) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for atomic database transactions.

        Automatically commits on success or rolls back on exception.
        If an external connection is passed, uses it without closing it.
        Otherwise creates a new connection and closes it on exit.
        """
        is_external = conn is not None
        connection = conn if is_external else self.get_connection()
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error("Transaction rolled back due to error: %s", e)
            raise
        finally:
            if not is_external:
                connection.close()

    def get_schema_version(self, conn: Optional[sqlite3.Connection] = None) -> int:
        """Return the current user_version pragma value."""

        def _get(c: sqlite3.Connection) -> int:
            cursor = c.execute("PRAGMA user_version;")
            row = cursor.fetchone()
            return int(row[0]) if row else 0

        if conn is not None:
            return _get(conn)
        with self.get_connection() as c:
            return _get(c)

    def set_schema_version(self, version: int, conn: sqlite3.Connection) -> None:
        """Set the user_version pragma value."""
        conn.execute(f"PRAGMA user_version = {int(version)};")

    def initialize_database(self) -> None:
        """Initialize database schema, apply pending migrations, and seed default data."""
        logger.info("Initializing database at %s", self.db_path)
        with self.get_connection() as conn:
            current_version = self.get_schema_version(conn)

            if current_version < 1:
                logger.info("Applying schema migration V1...")
                with conn:
                    for statement in SCHEMA_V1_STATEMENTS:
                        conn.execute(statement)
                    self.set_schema_version(1, conn)
                logger.info("Schema migration V1 applied successfully.")

            if current_version < 2:
                logger.info("Applying schema migration V2...")
                with conn:
                    for statement in SCHEMA_V2_STATEMENTS:
                        conn.execute(statement)
                    self.set_schema_version(2, conn)
                logger.info("Schema migration V2 applied successfully.")

            # Seed default categories if none exist
            self._seed_default_categories(conn)
            # Seed default account if none exists
            self._seed_default_account(conn)
            # Seed default user profile if none exists
            self._seed_default_user_profile(conn)

    def _seed_default_user_profile(self, conn: sqlite3.Connection) -> None:
        """Seed a default user profile row with empty name if none exists."""
        cursor = conn.execute("SELECT COUNT(*) as count FROM user_profile;")
        count = cursor.fetchone()["count"]
        if count == 0:
            logger.info("Seeding default empty user profile...")
            now = datetime.now().isoformat()
            with conn:
                conn.execute(
                    "INSERT INTO user_profile (id, name, created_at, updated_at) VALUES (1, NULL, ?, ?);",
                    (now, now),
                )
            logger.info("Default user profile seeded.")

    def _seed_default_categories(self, conn: sqlite3.Connection) -> None:
        """Seed default categories if category table is empty."""
        cursor = conn.execute("SELECT COUNT(*) as count FROM categories;")
        count = cursor.fetchone()["count"]
        if count == 0:
            logger.info("Seeding default categories...")
            now = datetime.now().isoformat()
            with conn:
                for name, cat_type in DEFAULT_CATEGORIES:
                    conn.execute(
                        "INSERT INTO categories (name, type, is_archived, created_at) VALUES (?, ?, 0, ?);",
                        (name, cat_type, now),
                    )
            logger.info("Default categories seeded successfully.")

    def _seed_default_account(self, conn: sqlite3.Connection) -> None:
        """Seed a default cash account if no accounts exist."""
        cursor = conn.execute("SELECT COUNT(*) as count FROM accounts;")
        count = cursor.fetchone()["count"]
        if count == 0:
            logger.info("Seeding default 'Dompet Tunai' account...")
            now = datetime.now().isoformat()
            with conn:
                conn.execute(
                    """
                    INSERT INTO accounts (name, account_type, opening_balance, created_at, is_archived)
                    VALUES (?, ?, ?, ?, 0);
                    """,
                    ("Dompet Tunai", "cash", 0, now),
                )
            logger.info("Default account seeded successfully.")

    def backup_database(self, destination_path: Path) -> Path:
        """Create a consistent snapshot backup using SQLite's backup API."""
        destination_path = Path(destination_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Backing up database to %s", destination_path)
        src_conn = self.get_connection()
        dest_conn = sqlite3.connect(str(destination_path))
        try:
            with dest_conn:
                src_conn.backup(dest_conn)
        finally:
            dest_conn.close()
            src_conn.close()
        logger.info("Database backup created successfully at %s", destination_path)
        return destination_path
