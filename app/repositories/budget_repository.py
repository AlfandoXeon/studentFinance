from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List, Optional

from app.database.database_manager import DatabaseManager
from app.models.budget import Budget


class BudgetRepository:
    """Repository for managing budgets in SQLite."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _row_to_model(self, row: sqlite3.Row) -> Budget:
        return Budget(
            id=row["id"],
            category_id=row["category_id"],
            amount=row["amount"],
            period_year=row["period_year"],
            period_month=row["period_month"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, budget: Budget, conn: Optional[sqlite3.Connection] = None) -> Budget:
        """Insert a budget record."""
        query = """
            INSERT INTO budgets (category_id, amount, period_year, period_month, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (
            budget.category_id,
            budget.amount,
            budget.period_year,
            budget.period_month,
            budget.created_at,
            budget.updated_at,
        )
        if conn is not None:
            cursor = conn.execute(query, params)
            budget.id = cursor.lastrowid
            return budget

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            budget.id = cursor.lastrowid
            return budget

    def get_by_id(self, budget_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[Budget]:
        """Fetch budget by ID."""
        query = "SELECT * FROM budgets WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (budget_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (budget_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_by_category_and_period(
        self, category_id: int, year: int, month: int, conn: Optional[sqlite3.Connection] = None
    ) -> Optional[Budget]:
        """Fetch budget for a specific category and period."""
        query = "SELECT * FROM budgets WHERE category_id = ? AND period_year = ? AND period_month = ?;"
        if conn is not None:
            cursor = conn.execute(query, (category_id, year, month))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (category_id, year, month))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def list_for_period(self, year: int, month: int, conn: Optional[sqlite3.Connection] = None) -> List[Budget]:
        """List all budgets for a given year and month."""
        query = """
            SELECT b.*, c.name as category_name
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.period_year = ? AND b.period_month = ?
            ORDER BY c.name ASC;
        """
        if conn is not None:
            cursor = conn.execute(query, (year, month))
            return [self._row_to_model(row) for row in cursor.fetchall()]

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (year, month))
            return [self._row_to_model(row) for row in cursor.fetchall()]

    def update(self, budget: Budget, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Update a budget amount."""
        if budget.id is None:
            raise ValueError("Budget ID cannot be None for update.")
        budget.updated_at = datetime.now().isoformat()
        query = "UPDATE budgets SET amount = ?, updated_at = ? WHERE id = ?;"
        params = (budget.amount, budget.updated_at, budget.id)
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            return cursor.rowcount > 0

    def delete(self, budget_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Delete a budget by ID."""
        query = "DELETE FROM budgets WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (budget_id,))
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, (budget_id,))
            return cursor.rowcount > 0
