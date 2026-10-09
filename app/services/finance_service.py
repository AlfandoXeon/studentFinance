from __future__ import annotations

import logging
from datetime import date
from typing import List, Optional, Tuple

from app.database.database_manager import DatabaseManager
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.utils.validators import (
    ValidationError,
    validate_iso_date,
    validate_positive_amount,
    validate_transfer_accounts,
)

logger = logging.getLogger(__name__)


class FinanceService:
    """Core financial business logic: accounts, categories, and transactions."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        account_repo: AccountRepository,
        category_repo: CategoryRepository,
        transaction_repo: TransactionRepository,
    ):
        self.db_manager = db_manager
        self.account_repo = account_repo
        self.category_repo = category_repo
        self.transaction_repo = transaction_repo

    # ---------------- Accounts ----------------

    def create_account(self, name: str, account_type: str, opening_balance: int = 0) -> Account:
        """Create a new account."""
        account = Account(name=name, account_type=account_type, opening_balance=opening_balance)
        return self.account_repo.create(account)

    def update_account(self, account_id: int, name: str, account_type: str, opening_balance: int) -> Account:
        """Update account details."""
        acc = self.account_repo.get_by_id(account_id)
        if not acc:
            raise ValidationError(f"Akun dengan ID {account_id} tidak ditemukan.")
        acc.name = name.strip()
        acc.account_type = account_type
        acc.opening_balance = opening_balance
        self.account_repo.update(acc)
        return acc

    def archive_account(self, account_id: int, is_archived: bool = True) -> bool:
        """Archive or unarchive an account."""
        acc = self.account_repo.get_by_id(account_id)
        if not acc:
            raise ValidationError(f"Akun dengan ID {account_id} tidak ditemukan.")
        return self.account_repo.set_archived(account_id, is_archived)

    def delete_account(self, account_id: int) -> bool:
        """Delete an account if it has no transactions."""
        return self.account_repo.delete(account_id)

    def list_accounts(self, include_archived: bool = False) -> List[Account]:
        """List active or all accounts."""
        return self.account_repo.list_all(include_archived=include_archived)

    def get_account_balance(self, account_id: int) -> int:
        """Calculate real-time balance of an account."""
        return self.transaction_repo.get_account_balance(account_id)

    def get_total_balance(self) -> int:
        """Calculate total balance across all active accounts."""
        return self.transaction_repo.get_total_balance_across_active_accounts()

    # ---------------- Categories ----------------

    def create_category(self, name: str, cat_type: str) -> Category:
        """Create a new category."""
        category = Category(name=name, type=cat_type)
        return self.category_repo.create(category)

    def update_category(self, category_id: int, name: str) -> Category:
        """Update category name."""
        cat = self.category_repo.get_by_id(category_id)
        if not cat:
            raise ValidationError(f"Kategori dengan ID {category_id} tidak ditemukan.")
        cat.name = name.strip()
        self.category_repo.update(cat)
        return cat

    def archive_category(self, category_id: int, is_archived: bool = True) -> bool:
        """Archive or unarchive a category."""
        cat = self.category_repo.get_by_id(category_id)
        if not cat:
            raise ValidationError(f"Kategori dengan ID {category_id} tidak ditemukan.")
        return self.category_repo.set_archived(category_id, is_archived)

    def delete_category(self, category_id: int) -> bool:
        """Delete a category if not referenced."""
        return self.category_repo.delete(category_id)

    def list_categories(self, cat_type: Optional[str] = None, include_archived: bool = False) -> List[Category]:
        """List categories, optionally filtered by type."""
        if cat_type:
            return self.category_repo.list_by_type(cat_type, include_archived=include_archived)
        return self.category_repo.list_all(include_archived=include_archived)

    # ---------------- Transactions ----------------

    def create_income(
        self,
        amount: int,
        account_id: int,
        category_id: int,
        transaction_date: str,
        description: Optional[str] = None,
    ) -> Transaction:
        """Record an income transaction."""
        amount = validate_positive_amount(amount)
        transaction_date = validate_iso_date(transaction_date)

        # Validate account exists
        acc = self.account_repo.get_by_id(account_id)
        if not acc:
            raise ValidationError("Akun sumber penerimaan tidak ditemukan.")
        if acc.is_archived:
            raise ValidationError("Tidak dapat mencatat transaksi pada akun yang diarsipkan.")

        # Validate category exists and is income
        cat = self.category_repo.get_by_id(category_id)
        if not cat:
            raise ValidationError("Kategori pemasukan tidak ditemukan.")
        if cat.type != "income":
            raise ValidationError(f"Kategori '{cat.name}' bukan kategori pemasukan.")

        txn = Transaction(
            type="income",
            amount=amount,
            account_id=account_id,
            category_id=category_id,
            transaction_date=transaction_date,
            description=description.strip() if description else None,
        )
        return self.transaction_repo.create(txn)

    def create_expense(
        self,
        amount: int,
        account_id: int,
        category_id: int,
        transaction_date: str,
        description: Optional[str] = None,
    ) -> Transaction:
        """Record an expense transaction."""
        amount = validate_positive_amount(amount)
        transaction_date = validate_iso_date(transaction_date)

        # Validate account exists
        acc = self.account_repo.get_by_id(account_id)
        if not acc:
            raise ValidationError("Akun pembayaran tidak ditemukan.")
        if acc.is_archived:
            raise ValidationError("Tidak dapat mencatat transaksi pada akun yang diarsipkan.")

        # Validate category exists and is expense
        cat = self.category_repo.get_by_id(category_id)
        if not cat:
            raise ValidationError("Kategori pengeluaran tidak ditemukan.")
        if cat.type != "expense":
            raise ValidationError(f"Kategori '{cat.name}' bukan kategori pengeluaran.")

        txn = Transaction(
            type="expense",
            amount=amount,
            account_id=account_id,
            category_id=category_id,
            transaction_date=transaction_date,
            description=description.strip() if description else None,
        )
        return self.transaction_repo.create(txn)

    def create_transfer(
        self,
        amount: int,
        source_account_id: int,
        dest_account_id: int,
        transaction_date: str,
        description: Optional[str] = None,
    ) -> Transaction:
        """Record an atomic transfer between two accounts."""
        amount = validate_positive_amount(amount)
        transaction_date = validate_iso_date(transaction_date)
        validate_transfer_accounts(source_account_id, dest_account_id)

        source_acc = self.account_repo.get_by_id(source_account_id)
        if not source_acc:
            raise ValidationError("Akun sumber transfer tidak ditemukan.")
        if source_acc.is_archived:
            raise ValidationError("Akun sumber transfer sedang diarsipkan.")

        dest_acc = self.account_repo.get_by_id(dest_account_id)
        if not dest_acc:
            raise ValidationError("Akun tujuan transfer tidak ditemukan.")
        if dest_acc.is_archived:
            raise ValidationError("Akun tujuan transfer sedang diarsipkan.")

        # Check balance of source account
        current_balance = self.transaction_repo.get_account_balance(source_account_id)
        if current_balance < amount:
            logger.warning(
                "Transfer amount %d exceeds current balance %d of account %s",
                amount,
                current_balance,
                source_acc.name,
            )
            # Depending on policy, we allow overdraft with warning or allow negative if configured,
            # but let's allow it with accurate math or reject. In cash/bank student life, balance warning
            # is important. Let's allow transfer but keep math accurate.

        txn = Transaction(
            type="transfer",
            amount=amount,
            account_id=source_account_id,
            to_account_id=dest_account_id,
            category_id=None,
            transaction_date=transaction_date,
            description=description.strip() if description else None,
        )
        return self.transaction_repo.create(txn)

    def update_transaction(self, transaction: Transaction) -> bool:
        """Validate and update an existing transaction."""
        existing = self.transaction_repo.get_by_id(transaction.id)
        if not existing:
            raise ValidationError(f"Transaksi ID {transaction.id} tidak ditemukan.")

        validate_positive_amount(transaction.amount)
        validate_iso_date(transaction.transaction_date)

        if transaction.type == "transfer":
            validate_transfer_accounts(transaction.account_id, transaction.to_account_id)
            transaction.category_id = None
        elif transaction.type in ("income", "expense"):
            transaction.to_account_id = None
            if transaction.category_id is None:
                raise ValidationError("Kategori wajib dipilih untuk transaksi pemasukan/pengeluaran.")
            cat = self.category_repo.get_by_id(transaction.category_id)
            if not cat or cat.type != transaction.type:
                raise ValidationError(f"Kategori tidak sesuai dengan tipe transaksi '{transaction.type}'.")

        return self.transaction_repo.update(transaction)

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction."""
        return self.transaction_repo.delete(transaction_id)

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID."""
        return self.transaction_repo.get_by_id(transaction_id)

    def list_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Transaction]:
        """List transactions with filters."""
        return self.transaction_repo.list_filtered(
            start_date=start_date,
            end_date=end_date,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            search_query=search_query,
            limit=limit,
            offset=offset,
        )

    def get_cashflow_summary(self, start_date: str, end_date: str) -> Tuple[int, int, int]:
        """Compute consolidated total income, total expenses, and net cashflow for a date range.

        Transfers are strictly excluded from consolidated income and expense.
        Returns: (total_income, total_expense, net_cashflow)
        """
        query = """
            SELECT
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
            FROM transactions
            WHERE transaction_date >= ? AND transaction_date <= ?;
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(query, (start_date, end_date))
            row = cursor.fetchone()
            inc = int(row["total_income"])
            exp = int(row["total_expense"])
            net = inc - exp
            return inc, exp, net

    def get_today_cashflow(self) -> Tuple[int, int]:
        """Get today's total income and total expense."""
        today_iso = date.today().isoformat()
        inc, exp, _ = self.get_cashflow_summary(today_iso, today_iso)
        return inc, exp
