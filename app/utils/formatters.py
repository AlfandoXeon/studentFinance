from __future__ import annotations

from datetime import date, datetime
from typing import Union

ID_MONTHS = [
    "",
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
]

ID_MONTHS_SHORT = [
    "",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
]


def format_currency(amount: int, prefix: str = "Rp ") -> str:
    """Format an integer rupiah value with thousands separators.

    Example: 1500000 -> "Rp 1.500.000", -50000 -> "-Rp 50.000"
    """
    if not isinstance(amount, int):
        raise TypeError(f"Amount must be an integer, got {type(amount).__name__}")

    if amount < 0:
        formatted = f"{abs(amount):,}".replace(",", ".")
        return f"-{prefix}{formatted}"

    formatted = f"{amount:,}".replace(",", ".")
    return f"{prefix}{formatted}"


def parse_currency(text: str) -> int:
    """Parse user input text into a positive integer rupiah amount.

    Handles 'Rp', dots, commas, spaces.
    Example: 'Rp 1.500.000' -> 1500000, '50000' -> 50000.
    Raises ValueError on invalid formats.
    """
    cleaned = text.strip().replace("Rp", "").replace("rp", "").replace(".", "").replace(",", "").replace(" ", "")
    if not cleaned:
        raise ValueError("Nominal tidak boleh kosong.")
    if not cleaned.isdigit():
        raise ValueError(f"Nominal harus berupa angka bulat positif, didapatkan: '{text}'")

    val = int(cleaned)
    if val <= 0:
        raise ValueError("Nominal harus lebih besar dari 0.")
    return val


def format_date_display(d: Union[str, date, datetime], short: bool = False) -> str:
    """Format date to friendly Indonesian format.

    Example: "2026-10-09" -> "09 Oktober 2026" or "09 Okt 2026"
    """
    if isinstance(d, str):
        # Extract YYYY-MM-DD
        clean_str = d[:10]
        dt = datetime.strptime(clean_str, "%Y-%m-%d").date()
    elif isinstance(d, datetime):
        dt = d.date()
    elif isinstance(d, date):
        dt = d
    else:
        raise TypeError(f"Expected str, date, or datetime, got {type(d).__name__}")

    months = ID_MONTHS_SHORT if short else ID_MONTHS
    return f"{dt.day:02d} {months[dt.month]} {dt.year}"
