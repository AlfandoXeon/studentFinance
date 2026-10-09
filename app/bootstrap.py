from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.config.settings import AppSettings
from app.database.database_manager import DatabaseManager
from app.repositories.account_repository import AccountRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_profile_repository import UserProfileRepository
from app.services.backup_service import BackupService
from app.services.budget_service import BudgetService
from app.services.finance_service import FinanceService
from app.services.report_service import ReportService
from app.services.survival_mode_service import SurvivalModeService
from app.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Dependency container holding initialized services and repositories."""

    settings: AppSettings
    db_manager: DatabaseManager
    account_repo: AccountRepository
    category_repo: CategoryRepository
    transaction_repo: TransactionRepository
    budget_repo: BudgetRepository
    user_profile_repo: UserProfileRepository
    finance_service: FinanceService
    budget_service: BudgetService
    report_service: ReportService
    survival_service: SurvivalModeService
    backup_service: BackupService


def bootstrap_application(custom_settings: Optional[AppSettings] = None) -> AppContext:
    """Initialize application settings, logging, database, repositories, and services."""
    settings = custom_settings or AppSettings()
    setup_logging(settings.logs_dir, settings.log_level)
    logger.info("Starting %s v%s...", settings.app_name, settings.version)

    # Database
    db_manager = DatabaseManager(settings.db_path)
    db_manager.initialize_database()

    # Repositories
    account_repo = AccountRepository(db_manager)
    category_repo = CategoryRepository(db_manager)
    transaction_repo = TransactionRepository(db_manager)
    budget_repo = BudgetRepository(db_manager)
    user_profile_repo = UserProfileRepository(db_manager)

    # Services
    finance_service = FinanceService(db_manager, account_repo, category_repo, transaction_repo)
    budget_service = BudgetService(db_manager, budget_repo, category_repo, settings.budget_warning_threshold)
    report_service = ReportService(db_manager, transaction_repo, category_repo, account_repo)
    survival_service = SurvivalModeService(transaction_repo)
    backup_service = BackupService(db_manager, settings.backup_dir)

    logger.info("Application bootstrap complete.")
    return AppContext(
        settings=settings,
        db_manager=db_manager,
        account_repo=account_repo,
        category_repo=category_repo,
        transaction_repo=transaction_repo,
        budget_repo=budget_repo,
        user_profile_repo=user_profile_repo,
        finance_service=finance_service,
        budget_service=budget_service,
        report_service=report_service,
        survival_service=survival_service,
        backup_service=backup_service,
    )
