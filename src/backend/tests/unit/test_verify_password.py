from __future__ import annotations
from unittest.mock import patch
import pytest
from participium.core.security import verify_password
from unittest.mock import Mock

# TC-1
@patch("participium.core.security.verify_password")
def test_verify_password_success(mock_verify: Mock) -> None:
    password = "psw20"
    password_hash = "HASH_PASSWORD_20"
    mock_verify.return_value = True

    result = verify_password(password, password_hash)

    assert result is True
    assert isinstance(result, bool)

# TC-2
@patch("participium.core.security.verify_password")
def test_verify_password_unsuccess(mock_verify: Mock) -> None:
    password = "psw20"
    password_hash = "HASH_SBAGLIATO"
    mock_verify.return_value = False

    result = verify_password(password, password_hash)

    assert result is False
    assert isinstance(result, bool)