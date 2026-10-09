# Student Finance Desktop Application

A desktop financial management application designed specifically for university students. Built with Python 3.12+, PySide6, and SQLite, following clean architecture principles (MVC + Service Layer + Repository Pattern).

## Key Features

- **Dashboard**: Net worth across accounts, monthly cash flow, category breakdown, quick transactions, and budget alerts.
- **Transaction Management**: Record income, expenses, and inter-account transfers in Indonesian Rupiah (IDR) with strict validation.
- **Account Management**: Cash, bank accounts, and e-wallets with automatic balance calculation from opening balances and transaction history.
- **Category Management**: Pre-seeded customizable income and expense categories.
- **Budget Management**: Monthly spending caps per category with threshold warnings and utilization metrics.
- **Financial Reports**: Date-filtered income vs expense analysis, category breakdown, highest spending, and CSV export.
- **Student Survival Mode**: Daily spending guidance and run-out estimates until the next expected income.
- **Data Protection & Backup**: Local SQLite storage, consistent backup and restore workflow.

## Architecture

The project follows a layered MVC architecture with clear separation of concerns:

```
View (PySide6) -> Controller -> Service -> Repository -> Database (SQLite)
```

- **Domain Models** (`app/models`): Pure Python dataclasses representing business entities. No GUI or database dependencies.
- **Repositories** (`app/repositories`): Data persistence and SQL queries using parameterized SQLite queries.
- **Services** (`app/services`): Authoritative financial rules, balance derivations, budget tracking, and survival calculations.
- **Controllers** (`app/controllers`): Bridge between views and services, normalizing inputs and refreshing UI state.
- **Views** (`app/views`): PySide6 interface following an elegant dark grey design system (no emojis, professional typography).

## Requirements

- Python 3.12+
- PySide6
- SQLite3 (built into Python standard library)

## Installation & Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Run automated tests:
   ```bash
   pytest
   ```

4. Code formatting and linting:
   ```bash
   ruff check .
   ruff format .
   ```
