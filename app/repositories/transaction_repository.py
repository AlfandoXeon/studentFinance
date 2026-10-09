from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any, List, Optional

from app.database.database_manager import DatabaseManager
from app.models.transaction import Transaction


class TransactionRepository:
    """Repository for managing financial transactions in SQLite."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _row_to_model(self, row: sqlite3.Row) -> Transaction:
        return Transaction(
            id=row["id"],
            type=row["type"],
            amount=row["amount"],
            account_id=row["account_id"],
            to_account_id=row["to_account_id"],
            category_id=row["category_id"],
            description=row["description"],
            transaction_date=row["transaction_date"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, transaction: Transaction, conn: Optional[sqlite3.Connection] = None) -> Transaction:
        """Insert a transaction record."""
        query = """
            INSERT INTO transactions (
                type, amount, account_id, to_account_id, category_id,
                description, transaction_date, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            transaction.type,
            transaction.amount,
            transaction.account_id,
            transaction.to_account_id,
            transaction.category_id,
            transaction.description,
            transaction.transaction_date,
            transaction.created_at,
            transaction.updated_at,
        )
        if conn is not None:
            cursor = conn.execute(query, params)
            transaction.id = cursor.lastrowid
            return transaction

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            transaction.id = cursor.lastrowid
            return transaction

    def get_by_id(self, transaction_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[Transaction]:
        """Fetch transaction by ID."""
        query = "SELECT * FROM transactions WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (transaction_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (transaction_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def list_filtered(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[Transaction]:
        """List transactions matching filter criteria."""
        conditions: List[str] = []
        params: List[Any] = []

        if start_date:
            conditions.append("transaction_date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("transaction_date <= ?")
            params.append(end_date)
        if account_id is not None:
            conditions.append("(account_id = ? OR to_account_id = ?)")
            params.extend([account_id, account_id])
        if category_id is not None:
            conditions.append("category_id = ?")
            params.append(category_id)
        if transaction_type:
            conditions.append("type = ?")
            params.append(transaction_type)
        if search_query:
            conditions.append("description LIKE ?")
            params.append(f"%{search_query.strip()}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT * FROM transactions {where_clause} ORDER BY transaction_date DESC, id DESC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)

        if conn is not None:
            cursor = conn.execute(query, tuple(params))
            return [self._row_to_model(row) for row in cursor.fetchall()]

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, tuple(params))
            return [self._row_to_model(row) for row in cursor.fetchall()]

    def update(self, transaction: Transaction, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Update an existing transaction."""
        if transaction.id is None:
            raise ValueError("Transaction ID cannot be None for update.")
        transaction.updated_at = datetime.now().isoformat()
        query = """
            UPDATE transactions
            SET type = ?, amount = ?, account_id = ?, to_account_id = ?,
                category_id = ?, description = ?, transaction_date = ?, updated_at = ?
            WHERE id = ?;
        """
        params = (
            transaction.type,
            transaction.amount,
            transaction.account_id,
            transaction.to_account_id,
            transaction.category_id,
            transaction.description,
            transaction.transaction_date,
            transaction.updated_at,
            transaction.id,
        )
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            return cursor.rowcount > 0

    def delete(self, transaction_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Delete a transaction by ID."""
        query = "DELETE FROM transactions WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (transaction_id,))
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, (transaction_id,))
            return cursor.rowcount > 0

    def get_account_balance(self, account_id: int, conn: Optional[sqlite3.Connection] = None) -> int:
        """Calculate the real-time balance of an account from opening balance and all transactions.

        Balance = Opening Balance + Income - Expenses + Transfers In - Transfers Out
        """
        query = """
            SELECT
                a.opening_balance,
                COALESCE((
                    SELECT SUM(amount) FROM transactions WHERE account_id = a.id AND type = 'income'
                ), 0) AS total_income,
                COALESCE((
                    SELECT SUM(amount) FROM transactions WHERE account_id = a.id AND type = 'expense'
                ), 0) AS total_expense,
                COALESCE((
                    SELECT SUM(amount) FROM transactions WHERE to_account_id = a.id AND type = 'transfer'
                ), 0) AS total_transfers_in,
                COALESCE((
                    SELECT SUM(amount) FROM transactions WHERE account_id = a.id AND type = 'transfer'
                ), 0) AS total_transfers_out
            FROM accounts a
            WHERE a.id = ?;
        """

        def _compute(c: sqlite3.Connection) -> int:
            cursor = c.execute(query, (account_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Akun dengan ID {account_id} tidak ditemukan.")
            return (
                row["opening_balance"]
                + row["total_income"]
                - row["total_expense"]
                + row["total_transfers_in"]
                - row["total_transfers_out"]
            )

        if conn is not None:
            return _compute(conn)

        with self.db_manager.get_connection() as c:
            return _compute(c)

    def get_total_balance_across_active_accounts(self, conn: Optional[sqlite3.Connection] = None) -> int:
        """Calculate total balance across all active (non-archived) accounts."""
        query_accounts = "SELECT id FROM accounts WHERE is_archived = 0;"
        if conn is not None:
            accounts = conn.execute(query_accounts).fetchall()
            return sum(self.get_account_balance(row["id"], conn) for row in accounts)

        with self.db_manager.get_connection() as c:
            accounts = c.execute(query_accounts).fetchall()
            return sum(self.get_account_balance(row["id"], c) for row in accounts)
