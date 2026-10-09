from __future__ import annotations

from PySide6.QtWidgets import QLineEdit


class CurrencyLineEdit(QLineEdit):
    """QLineEdit that automatically formats positive integer amounts with thousands separators

    live as the user types.
    """

    def __init__(self, separator: str = ",", parent=None):
        super().__init__(parent)
        self.separator = separator
        self.textEdited.connect(self._format_live)

    def _format_live(self, text: str) -> None:
        """Format digits with thousands separator while preserving cursor position."""
        cursor_pos = self.cursorPosition()
        text_before_cursor = text[:cursor_pos]
        digits_before_cursor = sum(1 for c in text_before_cursor if c.isdigit())

        # Strip all non-digit characters
        raw_digits = "".join(c for c in text if c.isdigit())
        if not raw_digits:
            self.blockSignals(True)
            self.setText("")
            self.blockSignals(False)
            return

        val = int(raw_digits)
        if self.separator == ",":
            formatted = f"{val:,}"
        else:
            formatted = f"{val:,}".replace(",", ".")

        self.blockSignals(True)
        self.setText(formatted)
        self.blockSignals(False)

        # Reposition cursor accurately after formatting
        new_cursor_pos = 0
        counted_digits = 0
        for i, c in enumerate(formatted):
            if counted_digits == digits_before_cursor:
                new_cursor_pos = i
                break
            if c.isdigit():
                counted_digits += 1
                new_cursor_pos = i + 1

        self.setCursorPosition(new_cursor_pos)

    def get_amount(self) -> int:
        """Return the current amount as an integer rupiah."""
        digits = "".join(c for c in self.text() if c.isdigit())
        return int(digits) if digits else 0

    def set_amount(self, amount: int) -> None:
        """Set an integer amount and format it with thousands separators."""
        if amount <= 0:
            self.setText("")
        else:
            if self.separator == ",":
                self.setText(f"{amount:,}")
            else:
                self.setText(f"{amount:,}".replace(",", "."))
