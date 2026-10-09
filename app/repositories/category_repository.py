from __future__ import annotations

import sqlite3
from typing import List, Optional

from app.database.database_manager import DatabaseManager
from app.models.category import Category


class CategoryRepository:
    """Repository for managing category records in SQLite."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _row_to_model(self, row: sqlite3.Row) -> Category:
        return Category(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            is_archived=bool(row["is_archived"]),
            created_at=row["created_at"],
        )

    def create(self, category: Category, conn: Optional[sqlite3.Connection] = None) -> Category:
        """Insert a new category."""
        query = "INSERT INTO categories (name, type, is_archived, created_at) VALUES (?, ?, ?, ?);"
        params = (
            category.name,
            category.type,
            1 if category.is_archived else 0,
            category.created_at,
        )
        if conn is not None:
            cursor = conn.execute(query, params)
            category.id = cursor.lastrowid
            return category

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            category.id = cursor.lastrowid
            return category

    def get_by_id(self, category_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[Category]:
        """Fetch category by ID."""
        query = "SELECT * FROM categories WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (category_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (category_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def list_by_type(
        self,
        category_type: str,
        include_archived: bool = False,
        conn: Optional[sqlite3.Connection] = None,
    ) -> List[Category]:
        """List categories by type ('income' or 'expense')."""
        if include_archived:
            query = "SELECT * FROM categories WHERE type = ? ORDER BY name ASC;"
            params = (category_type,)
        else:
            query = "SELECT * FROM categories WHERE type = ? AND is_archived = 0 ORDER BY name ASC;"
            params = (category_type,)

        if conn is not None:
            cursor = conn.execute(query, params)
            return [self._row_to_model(row) for row in cursor.fetchall()]

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, params)
            return [self._row_to_model(row) for row in cursor.fetchall()]

    def list_all(self, include_archived: bool = False, conn: Optional[sqlite3.Connection] = None) -> List[Category]:
        """List all categories."""
        if include_archived:
            query = "SELECT * FROM categories ORDER BY type ASC, name ASC;"
            params = ()
        else:
            query = "SELECT * FROM categories WHERE is_archived = 0 ORDER BY type ASC, name ASC;"
            params = ()

        if conn is not None:
            cursor = conn.execute(query, params)
            return [self._row_to_model(row) for row in cursor.fetchall()]

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, params)
            return [self._row_to_model(row) for row in cursor.fetchall()]

    def update(self, category: Category, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Update category name and archived state. Type should generally remain immutable."""
        if category.id is None:
            raise ValueError("Category ID cannot be None for update.")
        query = "UPDATE categories SET name = ?, is_archived = ? WHERE id = ?;"
        params = (category.name, 1 if category.is_archived else 0, category.id)
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            return cursor.rowcount > 0

    def set_archived(self, category_id: int, is_archived: bool, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Archive or unarchive a category."""
        query = "UPDATE categories SET is_archived = ? WHERE id = ?;"
        params = (1 if is_archived else 0, category_id)
        if conn is not None:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, params)
            return cursor.rowcount > 0

    def has_transactions_or_budgets(self, category_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Check if category is referenced by any transaction or budget."""
        query = """
            SELECT 1 FROM transactions WHERE category_id = ?
            UNION ALL
            SELECT 1 FROM budgets WHERE category_id = ?
            LIMIT 1;
        """
        if conn is not None:
            cursor = conn.execute(query, (category_id, category_id))
            return cursor.fetchone() is not None

        with self.db_manager.get_connection() as c:
            cursor = c.execute(query, (category_id, category_id))
            return cursor.fetchone() is not None

    def delete(self, category_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Delete category if not referenced anywhere."""
        if self.has_transactions_or_budgets(category_id, conn):
            raise ValueError(
                "Kategori tidak dapat dihapus karena digunakan dalam transaksi atau anggaran. "
                "Arsipkan kategori sebagai gantinya."
            )
        query = "DELETE FROM categories WHERE id = ?;"
        if conn is not None:
            cursor = conn.execute(query, (category_id,))
            return cursor.rowcount > 0

        with self.db_manager.transaction() as c:
            cursor = c.execute(query, (category_id,))
            return cursor.rowcount > 0
