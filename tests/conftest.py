from __future__ import annotations

from pathlib import Path

import pytest

from app.bootstrap import AppContext, bootstrap_application
from app.config.settings import AppSettings


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Fixture providing a temporary database file path."""
    return tmp_path / "test_finance.db"


@pytest.fixture
def temp_backup_dir(tmp_path: Path) -> Path:
    """Fixture providing a temporary backup directory."""
    b_dir = tmp_path / "backups"
    b_dir.mkdir(parents=True, exist_ok=True)
    return b_dir


@pytest.fixture
def temp_logs_dir(tmp_path: Path) -> Path:
    """Fixture providing a temporary logs directory."""
    l_dir = tmp_path / "logs"
    l_dir.mkdir(parents=True, exist_ok=True)
    return l_dir


@pytest.fixture
def app_context(temp_db_path: Path, temp_backup_dir: Path, temp_logs_dir: Path) -> AppContext:
    """Fixture initializing an isolated test AppContext."""
    settings = AppSettings(
        db_path=temp_db_path,
        backup_dir=temp_backup_dir,
        logs_dir=temp_logs_dir,
        log_level="DEBUG",
    )
    return bootstrap_application(settings)
