from __future__ import annotations

from datetime import datetime
import pytest

from participium.core.utils import parse_date

# --- COSTANTI ORIGINALI ---
CORRECT_DATETIME = datetime(2026, 4, 20)

# TC-1
def test_parse_date_NON_ISO8601_unsuccess() -> None:
    date_value = "32/13-210"

    with pytest.raises(ValueError):
        parse_date(date_value)


# TC-2
def test_parse_date_empty_returns_none() -> None:
    date_value = ""

    verified_date = parse_date(date_value)

    assert verified_date is None


# TC-3
def test_parse_date_success() -> None:
    date_value = "2026-04-20"

    verified_date = parse_date(date_value)

    assert isinstance(verified_date, datetime)
    assert verified_date == CORRECT_DATETIME
    

# TC-4
def test_parse_date_None_returns_none() -> None:
    date_value = None

    verified_date = parse_date(date_value)

    assert verified_date is None