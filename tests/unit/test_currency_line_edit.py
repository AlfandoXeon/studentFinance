from __future__ import annotations

from app.ui.components.currency_line_edit import CurrencyLineEdit


def test_currency_line_edit_formatting(qtbot):
    edit = CurrencyLineEdit()
    qtbot.addWidget(edit)

    # Set amount programmatically
    edit.set_amount(1000)
    assert edit.text() == "1,000"
    assert edit.get_amount() == 1000

    edit.set_amount(100000)
    assert edit.text() == "100,000"
    assert edit.get_amount() == 100000

    edit.set_amount(1500000)
    assert edit.text() == "1,500,000"
    assert edit.get_amount() == 1500000

    # Test live typing simulation
    edit.clear()
    edit._format_live("1000")
    assert edit.text() == "1,000"
    assert edit.get_amount() == 1000

    edit._format_live("100000")
    assert edit.text() == "100,000"
    assert edit.get_amount() == 100000

    # Non-digit filtering
    edit._format_live("Rp 50.000")
    assert edit.text() == "50,000"
    assert edit.get_amount() == 50000

    # Empty
    edit._format_live("")
    assert edit.text() == ""
    assert edit.get_amount() == 0
