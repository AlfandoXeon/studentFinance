from __future__ import annotations

from typing import Any, Dict, List

from app.bootstrap import AppContext
from app.models.account import Account


class AccountController:
    """Controller for account management."""

    def __init__(self, context: AppContext):
        self.context = context

    def list_accounts_with_balances(self, include_archived: bool = True) -> List[Dict[str, Any]]:
        """List accounts along with their real-time calculated balances."""
        accounts = self.context.finance_service.list_accounts(include_archived=include_archived)
        results = []
        for acc in accounts:
            bal = self.context.finance_service.get_account_balance(acc.id)
            has_history = self.context.account_repo.has_transactions(acc.id)
            results.append(
                {
                    "account": acc,
                    "current_balance": bal,
                    "has_history": has_history,
                }
            )
        return results

    def create_account(self, name: str, account_type: str, opening_balance: int) -> Account:
        return self.context.finance_service.create_account(name, account_type, opening_balance)

    def update_account(self, account_id: int, name: str, account_type: str, opening_balance: int) -> Account:
        return self.context.finance_service.update_account(account_id, name, account_type, opening_balance)

    def archive_account(self, account_id: int, is_archived: bool) -> bool:
        return self.context.finance_service.archive_account(account_id, is_archived)

    def delete_account(self, account_id: int) -> bool:
        return self.context.finance_service.delete_account(account_id)
