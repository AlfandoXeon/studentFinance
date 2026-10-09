from __future__ import annotations

from typing import List, Tuple

CURRENT_SCHEMA_VERSION = 2

SCHEMA_V1_STATEMENTS: List[str] = [
    """
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        account_type TEXT NOT NULL CHECK(account_type IN ('cash', 'bank', 'e_wallet')),
        opening_balance INTEGER NOT NULL DEFAULT 0 CHECK(opening_balance >= 0),
        created_at TEXT NOT NULL,
        is_archived INTEGER NOT NULL DEFAULT 0 CHECK(is_archived IN (0, 1))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
        is_archived INTEGER NOT NULL DEFAULT 0 CHECK(is_archived IN (0, 1)),
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'transfer')),
        amount INTEGER NOT NULL CHECK(amount > 0),
        account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
        to_account_id INTEGER NULL REFERENCES accounts(id) ON DELETE RESTRICT,
        category_id INTEGER NULL REFERENCES categories(id) ON DELETE RESTRICT,
        description TEXT NULL,
        transaction_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        CHECK (
            (type = 'transfer' AND to_account_id IS NOT NULL AND account_id != to_account_id AND category_id IS NULL)
            OR
            (type IN ('income', 'expense') AND to_account_id IS NULL)
        )
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
        amount INTEGER NOT NULL CHECK(amount > 0),
        period_year INTEGER NOT NULL CHECK(period_year >= 2000),
        period_month INTEGER NOT NULL CHECK(period_month BETWEEN 1 AND 12),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(category_id, period_year, period_month)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);",
    "CREATE INDEX IF NOT EXISTS idx_transactions_to_account ON transactions(to_account_id);",
    "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);",
    "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);",
    "CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period_year, period_month);",
    "CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type, is_archived);",
]

SCHEMA_V2_STATEMENTS: List[str] = [
    """
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY CHECK(id = 1),
        name TEXT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
]

DEFAULT_CATEGORIES: List[Tuple[str, str]] = [
    # Expense categories (name, type)
    ("Makanan & Minuman", "expense"),
    ("Tempat Tinggal & Kos", "expense"),
    ("Transportasi", "expense"),
    ("Pendidikan & Kuliah", "expense"),
    ("Internet & Pulsa", "expense"),
    ("Kebutuhan Pribadi", "expense"),
    ("Hiburan & Rekreasi", "expense"),
    ("Kesehatan & Medis", "expense"),
    ("Langganan", "expense"),
    ("Pengeluaran Lainnya", "expense"),
    # Income categories (name, type)
    ("Uang Saku", "income"),
    ("Gaji & Pekerjaan", "income"),
    ("Freelance & Proyek", "income"),
    ("Beasiswa", "income"),
    ("Pemasukan Lainnya", "income"),
]
