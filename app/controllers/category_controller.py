from __future__ import annotations

from typing import List, Optional

from app.bootstrap import AppContext
from app.models.category import Category


class CategoryController:
    """Controller for category management."""

    def __init__(self, context: AppContext):
        self.context = context

    def list_categories(self, cat_type: Optional[str] = None, include_archived: bool = True) -> List[Category]:
        return self.context.finance_service.list_categories(cat_type=cat_type, include_archived=include_archived)

    def create_category(self, name: str, cat_type: str) -> Category:
        return self.context.finance_service.create_category(name=name, cat_type=cat_type)

    def update_category(self, category_id: int, name: str) -> Category:
        return self.context.finance_service.update_category(category_id=category_id, name=name)

    def archive_category(self, category_id: int, is_archived: bool) -> bool:
        return self.context.finance_service.archive_category(category_id=category_id, is_archived=is_archived)

    def delete_category(self, category_id: int) -> bool:
        return self.context.finance_service.delete_category(category_id=category_id)
