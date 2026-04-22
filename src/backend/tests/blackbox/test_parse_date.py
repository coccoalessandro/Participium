from __future__ import annotations

from participium.core.utils import parse_date
from datetime import datetime

import pytest

# Function: parse_date
# Inputs: value(str | None)
# Expected Output:
# - Parsed datetime when value is non-empty and valid ISO-8601 datetime string.
# - None when value is None or empty string.
# - ValueError when value is non-empty but not a valid ISO-8601 datetime string
#def parse_date(value: str | None) -> datetime | None

CORRECT_DATETIME = datetime(2026, 4, 20)

#TC-1
def test_parse_date_NON_ISO8601_unsuccess(seed_parse_date_data: None) -> None:
    date_value = "32/13-210"

    with pytest.raises(ValueError):
        parse_date(date_value)


#TC-2
def test_parse_date_empty_returns_none(seed_parse_date_data: None) -> None:
    date_value = ""

    verified_date = parse_date(date_value)

    assert verified_date is None


#TC-3
def test_parse_date_success(seed_parse_date_data: None) -> None:
    date_value = "2026-04-20"

    verified_date = parse_date(date_value)

    assert isinstance(verified_date, datetime)
    assert verified_date == CORRECT_DATETIME
    

#TC-4
def test_parse_date_None_returns_none(seed_parse_date_data: None) -> None:
    date_value = None

    verified_date = parse_date(date_value)

    assert verified_date is None