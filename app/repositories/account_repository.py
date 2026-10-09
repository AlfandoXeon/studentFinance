from __future__ import annotations

import sqlite3
from typing import List, Optional

from app.database.database_manager import DatabaseManager
from app.models.account import Account


class AccountRepository:
    """Repository for managing account records in SQLite."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _row_to_model(self, row: sqlite3.Row) -> Account:
        return Account(
            id=row["id"],
            name=row["name"],
            account_type=row["account_type"],
            opening_balance=row["opening_balance"],
            created_at=row["created_at"],
            is_archived=bool(row["is_archived"]),
        )

    def create(self, account: Account, conn: Optional[sqlite3.Connection] = None) -> Account:
        """Insert a new account into the database."""
        query = """
            INSERT INTO accounts (name, account_type, opening_balance, created_at, is_archived)
            VALUES (?, ?, ?, ?, ?);
        """
        params = (
            account.name,
            account.account_type,
            account.opening_balance,
            account.created_at,
            1 if account.is_archived else 0,
        )
        if conn is not None:
            cursor = conn.execute(query, params)
            account.id = cursor.lastrowid
            return account

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            account.id = cursor.lastrowid
            return account

    def get_by_id(self, account_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[Account]:
        """Fetch an account by ID."""
        query = "SELECT * FROM accounts WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (account_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (account_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def list_all(self, include_archived: bool = False, conn: Optional[sqlite3.Connection] = None) -> List[Account]:
        """List all accounts, optionally including archived accounts."""
        if include_archived:
            query = "SELECT * FROM accounts ORDER BY id ASC;"
            params = ()
        else:
            query = "SELECT * FROM accounts WHERE is_archived = 0 ORDER BY id ASC;"
            params = ()

        if conn is not None:
            cursor = conn.execute(query, params)
            return [self._row_to_model(row) for row in cursor.fetchall()]

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, params)
            return [self._row_to_model(row) for row in cursor.fetchall()]

    def update(self, account: Account, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Update an existing account's name, type, and opening balance."""
        if account.id is None:
            raise ValueError("Account ID cannot be None for update.")
        query = """
            UPDATE accounts
            SET name = ?, account_type = ?, opening_balance = ?, is_archived = ?
            WHERE id = ?;
        """
        params = (
            account.name,
            account.account_type,
            account.opening_balance,
            1 if account.is_archived else 0,
            account.id,
        )
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            return cursor.rowcount > 0

    def set_archived(self, account_id: int, is_archived: bool, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Archive or unarchive an account."""
        query = "UPDATE accounts SET is_archived = ? WHERE id = ?;"
        params = (1 if is_archived else 0, account_id)
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            return cursor.rowcount > 0

    def has_transactions(self, account_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Check if an account has any associated transactions."""
        query = "SELECT 1 FROM transactions WHERE account_id = ? OR to_account_id = ? LIMIT 1;"
        if conn is not None:
            cursor = conn.execute(query, (account_id, account_id))
            return cursor.fetchone() is not None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (account_id, account_id))
            return cursor.fetchone() is not None

    def delete(self, account_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Delete an account if it has no financial history."""
        if self.has_transactions(account_id, conn):
            raise ValueError(
                "Akun tidak dapat dihapus karena memiliki riwayat transaksi. Arsipkan akun sebagai gantinya."
            )
        query = "DELETE FROM accounts WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (account_id,))
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, (account_id,))
            return cursor.rowcount > 0
