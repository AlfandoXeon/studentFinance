from __future__ import annotations

from typing import List, Optional

from app.bootstrap import AppContext
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction


class TransactionController:
    """Controller managing transactions and filters."""

    def __init__(self, context: AppContext):
        self.context = context

    def get_accounts(self, include_archived: bool = False) -> List[Account]:
        return self.context.finance_service.list_accounts(include_archived=include_archived)

    def get_categories(self, cat_type: Optional[str] = None, include_archived: bool = False) -> List[Category]:
        return self.context.finance_service.list_categories(cat_type=cat_type, include_archived=include_archived)

    def list_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Transaction]:
        return self.context.finance_service.list_transactions(
            start_date=start_date,
            end_date=end_date,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            search_query=search_query,
        )

    def create_transaction(self, data: dict) -> Transaction:
        t_type = data["type"]
        amount = data["amount"]
        account_id = data["account_id"]
        transaction_date = data["transaction_date"]
        description = data.get("description")

        if t_type == "income":
            return self.context.finance_service.create_income(
                amount=amount,
                account_id=account_id,
                category_id=data["category_id"],
                transaction_date=transaction_date,
                description=description,
            )
        elif t_type == "expense":
            return self.context.finance_service.create_expense(
                amount=amount,
                account_id=account_id,
                category_id=data["category_id"],
                transaction_date=transaction_date,
                description=description,
            )
        elif t_type == "transfer":
            return self.context.finance_service.create_transfer(
                amount=amount,
                source_account_id=account_id,
                dest_account_id=data["to_account_id"],
                transaction_date=transaction_date,
                description=description,
            )
        else:
            raise ValueError(f"Tipe transaksi tidak valid: {t_type}")

    def update_transaction(self, transaction: Transaction) -> bool:
        return self.context.finance_service.update_transaction(transaction)

    def delete_transaction(self, transaction_id: int) -> bool:
        return self.context.finance_service.delete_transaction(transaction_id)

    def export_csv(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
    ) -> str:
        return self.context.report_service.export_transactions_to_csv(
            start_date=start_date,
            end_date=end_date,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
        )
