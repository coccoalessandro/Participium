from __future__ import annotations

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from participium.core.exceptions import AuthenticationError, ValidationError
from participium.core.utils import utcnow
from participium.models.user import User
from participium.services.auth_service import AuthService



VALID_TOKEN = "VALID_TOKEN_FOR_MARIA_ROSSI"
ALREADY_USED_TOKEN = "ALREADY_USED_TOKEN"
EXPIRED_TOKEN = "EXPIRED_TOKEN_FOR_GIULIA_NERI"
NONEXISTENT_TOKEN = "NONEXISTENT_TOKEN"

VALID_PAYLOAD = {
    "username": "luca.bianchi",
    "first_name": "Luca",
    "last_name": "Bianchi",
    "email": "luca.bianchi@example.com",
    "password": "12345678",
}

VERIFICATION_BASE_URL = "https://example.com/verify"


def _user(
    *,
    user_id: int,
    username: str,
    email: str,
    is_active: bool = True,
    is_email_verified: bool = True,
) -> User:
    return User(
        id=user_id,
        username=username,
        first_name="Nome",
        last_name="Cognome",
        email=email,
        password_hash=f"HASHED_PASSWORD_{user_id}",
        is_active=is_active,
        is_email_verified=is_email_verified,
    )


@pytest.fixture
def auth_bundle() -> dict[str, object]:
    session = Mock()
    user_repository = Mock()
    token_repository = Mock()
    email_gateway = Mock()

    service = AuthService(
        session=session,
        user_repository=user_repository,
        token_repository=token_repository,
        email_gateway=email_gateway,
    )

    return {
        "service": service,
        "session": session,
        "user_repository": user_repository,
        "token_repo": token_repository,
        "email_gateway": email_gateway,
    }



@pytest.fixture
def user_not_found_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    auth_bundle["user_repository"].get_by_username_or_email.return_value = None
    return auth_bundle


@pytest.fixture
def correct_user_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(user_id=102, username="luca.bianchi", email="luca.bianchi@example.com")
    auth_bundle["user_repository"].get_by_username_or_email.return_value = user
    auth_bundle["user"] = user
    return auth_bundle


@pytest.fixture
def unverified_user_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(
        user_id=101,
        username="maria.rossi",
        email="maria.rossi@example.com",
        is_email_verified=False,
    )
    auth_bundle["user_repository"].get_by_username_or_email.return_value = user
    auth_bundle["user"] = user
    return auth_bundle


@pytest.fixture
def inactive_user_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(
        user_id=103,
        username="giulia.neri",
        email="giulia.neri@example.com",
        is_active=False,
    )
    auth_bundle["user_repository"].get_by_username_or_email.return_value = user
    auth_bundle["user"] = user
    return auth_bundle


def test_authenticate_empty_identifier_raises(user_not_found_case: dict[str, object]) -> None:
    service = user_not_found_case["service"]

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("", "password")


@patch("participium.services.auth_service.verify_password")
def test_authenticate_empty_password_raises(
    mock_verify_password, correct_user_case: dict[str, object]
) -> None:
    mock_verify_password.return_value = False
    service = correct_user_case["service"]

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("luca.bianchi", "")


def test_authenticate_unknown_identifier_raises(user_not_found_case: dict[str, object]) -> None:
    service = user_not_found_case["service"]

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("utente.inesistente", "password")


@patch("participium.services.auth_service.verify_password")
def test_authenticate_wrong_password_raises(
    mock_verify_password, correct_user_case: dict[str, object]
) -> None:
    mock_verify_password.return_value = False
    service = correct_user_case["service"]

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("luca.bianchi", "password_errata")


@patch("participium.services.auth_service.verify_password")
def test_authenticate_by_username_success(
    mock_verify_password, correct_user_case: dict[str, object]
) -> None:
    mock_verify_password.return_value = True
    service = correct_user_case["service"]
    expected = correct_user_case["user"]

    result = service.authenticate("luca.bianchi", "password")

    assert isinstance(result, User)
    assert result.id == expected.id
    assert result.username == expected.username
    assert result.is_email_verified is True


@patch("participium.services.auth_service.verify_password")
def test_authenticate_by_email_success(
    mock_verify_password, correct_user_case: dict[str, object]
) -> None:
    mock_verify_password.return_value = True
    service = correct_user_case["service"]
    expected = correct_user_case["user"]

    result = service.authenticate("luca.bianchi@example.com", "password")

    assert isinstance(result, User)
    assert result.email == expected.email


@patch("participium.services.auth_service.verify_password")
def test_authenticate_unverified_email_raises(
    mock_verify_password, unverified_user_case: dict[str, object]
) -> None:
    mock_verify_password.return_value = True
    service = unverified_user_case["service"]

    with pytest.raises(AuthenticationError, match="Email verification is required before login."):
        service.authenticate("maria.rossi", "password")


def test_authenticate_inactive_user_raises(inactive_user_case: dict[str, object]) -> None:
    service = inactive_user_case["service"]

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("giulia.neri", "password")

@pytest.fixture
def pending_user() -> User:
    return User(
        id=101,
        username="maria.rossi",
        first_name="Maria",
        last_name="Rossi",
        email="maria.rossi@example.com",
        is_email_verified=False,
    )


@pytest.fixture
def valid_token_case(auth_bundle: dict[str, object], pending_user: User) -> dict[str, object]:
    mock_token = Mock()
    mock_token.token = VALID_TOKEN
    mock_token.is_used = False
    mock_token.expires_at = utcnow() + timedelta(hours=1)
    mock_token.user = pending_user
    auth_bundle["token_repo"].get_by_token.return_value = mock_token
    auth_bundle["token"] = mock_token
    return auth_bundle


@pytest.fixture
def nonexistent_token_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    auth_bundle["token_repo"].get_by_token.return_value = None
    return auth_bundle


@pytest.fixture
def already_used_token_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    mock_token = Mock()
    mock_token.is_used = True
    auth_bundle["token_repo"].get_by_token.return_value = mock_token
    auth_bundle["token"] = mock_token
    return auth_bundle


@pytest.fixture
def expired_token_case(auth_bundle: dict[str, object], pending_user: User) -> dict[str, object]:
    mock_token = Mock()
    mock_token.is_used = False
    mock_token.expires_at = utcnow() - timedelta(hours=1)
    mock_token.user = pending_user
    auth_bundle["token_repo"].get_by_token.return_value = mock_token
    auth_bundle["token"] = mock_token
    return auth_bundle


def test_verify_email_success(valid_token_case: dict[str, object]) -> None:
    service = valid_token_case["service"]
    token = valid_token_case["token"]
    session = valid_token_case["session"]

    verified_user = service.verify_email(VALID_TOKEN)

    assert isinstance(verified_user, User)
    assert verified_user.id == 101
    assert verified_user.is_email_verified is True
    assert token.is_used is True
    session.commit.assert_called_once()


def test_verify_email_nonexistent_token_raises(nonexistent_token_case: dict[str, object]) -> None:
    service = nonexistent_token_case["service"]

    with pytest.raises(ValidationError):
        service.verify_email(NONEXISTENT_TOKEN)


def test_verify_email_already_used_token_raises(already_used_token_case: dict[str, object]) -> None:
    service = already_used_token_case["service"]

    with pytest.raises(ValidationError):
        service.verify_email(ALREADY_USED_TOKEN)


def test_verify_email_expired_token_raises(expired_token_case: dict[str, object]) -> None:
    service = expired_token_case["service"]

    with pytest.raises(ValidationError):
        service.verify_email(EXPIRED_TOKEN)


@pytest.fixture
def no_conflicts_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    auth_bundle["user_repository"].get_by_username.return_value = None
    auth_bundle["user_repository"].get_by_email.return_value = None
    return auth_bundle


@pytest.fixture
def duplicate_username_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    existing = Mock(spec=User)
    existing.username = VALID_PAYLOAD["username"]
    auth_bundle["user_repository"].get_by_username.return_value = existing
    return auth_bundle


@pytest.fixture
def duplicate_email_case(auth_bundle: dict[str, object]) -> dict[str, object]:
    existing = Mock(spec=User)
    existing.email = VALID_PAYLOAD["email"]
    auth_bundle["user_repository"].get_by_username.return_value = None
    auth_bundle["user_repository"].get_by_email.return_value = existing
    return auth_bundle

def test_register_user_missing_fields_raises(auth_bundle: dict[str, object]) -> None:
    service = auth_bundle["service"]

    with pytest.raises(ValidationError, match="Missing required fields"):
        service.register_user({"username": "solo_username"})


def test_register_user_duplicate_username_raises(duplicate_username_case: dict[str, object]) -> None:
    service = duplicate_username_case["service"]

    with pytest.raises(ValidationError, match="Username already in use."):
        service.register_user(VALID_PAYLOAD)


def test_register_user_duplicate_email_raises(duplicate_email_case: dict[str, object]) -> None:
    service = duplicate_email_case["service"]

    with pytest.raises(ValidationError, match="Email already in use."):
        service.register_user(VALID_PAYLOAD)


def test_register_user_with_verification_url_success(no_conflicts_case: dict[str, object]) -> None:
    service = no_conflicts_case["service"]
    email_gateway = no_conflicts_case["email_gateway"]

    result_user, verification_url = service.register_user(VALID_PAYLOAD, VERIFICATION_BASE_URL)

    assert isinstance(result_user, User)
    assert result_user.username == VALID_PAYLOAD["username"]
    assert result_user.first_name == VALID_PAYLOAD["first_name"]
    assert result_user.last_name == VALID_PAYLOAD["last_name"]
    assert result_user.email == VALID_PAYLOAD["email"]
    assert isinstance(verification_url, str)
    assert verification_url.startswith(VERIFICATION_BASE_URL)
    email_gateway.send.assert_called_once()


def test_register_user_without_verification_url_success(no_conflicts_case: dict[str, object]) -> None:
    service = no_conflicts_case["service"]
    email_gateway = no_conflicts_case["email_gateway"]

    result_user, verification_url = service.register_user(VALID_PAYLOAD, None)

    assert isinstance(result_user, User)
    assert result_user.username == VALID_PAYLOAD["username"]
    assert verification_url is None
    email_gateway.send.assert_not_called()