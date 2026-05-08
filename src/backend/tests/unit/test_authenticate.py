from __future__ import annotations

from unittest.mock import Mock, patch
import pytest

from participium.core.exceptions import AuthenticationError, ValidationError
from participium.models.user import User
from participium.services.auth_service import AuthService
from datetime import timedelta
from participium.core.utils import utcnow

# --- COSTANTI ORIGINALI ---

PENDING_VERIFICATION_USER = User(
    id=101,
    username="maria.rossi",
    first_name="Maria",
    last_name="Rossi",
    email="maria.rossi@example.com",
    password_hash="HASHED_PASSWORD_101",
    is_active=True,
    is_email_verified=False,
)

CORRECT_USER = User(
    id=102,
    username="luca.bianchi",
    first_name="Luca",
    last_name="Bianchi",
    email="luca.bianchi@example.com",
    password_hash="HASHED_PASSWORD_102",
    is_active=True,
    is_email_verified=True,
)

UNACTIVE_VERIFIED_USER = User(
    id=103,
    username="giulia.neri",
    first_name="Giulia",
    last_name="Neri",
    email="giulia.neri@example.com",
    password_hash="HASHED_PASSWORD_103",
    is_active=False,
    is_email_verified=True,
)

# --- FIXTURE DEL SERVIZIO ---

@pytest.fixture
def auth_service_bundle() -> dict[str, object]:
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
        "user_repository": user_repository,
    }


# --- TEST CASES MANTENENDO I TUOI NOMI ORIGINALI ---

# TC-1
def test_authenticate_empty_identifier_unsuccess(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = None

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("", "password")

# TC-2
@patch("participium.services.auth_service.verify_password")
def test_authenticate_empty_password_unsuccess(mock_verify_password, auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = CORRECT_USER
    mock_verify_password.return_value = False  # La password vuota non passa la verifica

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("luca.bianchi", "")
    
# TC-3
def test_authenticate_wrong_identifier_unsuccess(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = None

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("pippo", "password")

# TC-4
@patch("participium.services.auth_service.verify_password")
def test_authenticate_wrong_password_unsuccess(mock_verify_password, auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = CORRECT_USER
    mock_verify_password.return_value = False

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("luca.bianchi", "psw")

# TC-5
@patch("participium.services.auth_service.verify_password")
def test_authenticate_username_success(mock_verify_password, auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = CORRECT_USER
    mock_verify_password.return_value = True

    verified_user = service.authenticate("luca.bianchi", "password")

    assert isinstance(verified_user, User)
    assert verified_user.id == CORRECT_USER.id
    assert verified_user.username == CORRECT_USER.username
    assert verified_user.is_email_verified is True

# TC-6
@patch("participium.services.auth_service.verify_password")
def test_authenticate_email_success(mock_verify_password, auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = CORRECT_USER
    mock_verify_password.return_value = True

    verified_user = service.authenticate("luca.bianchi@example.com", "password")

    assert isinstance(verified_user, User)
    assert verified_user.email == CORRECT_USER.email

# TC-7
@patch("participium.services.auth_service.verify_password")
def test_authenticate_unverified_email_unsuccess(mock_verify_password, auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = PENDING_VERIFICATION_USER
    mock_verify_password.return_value = True

    with pytest.raises(AuthenticationError, match="Email verification is required before login."):
        service.authenticate("maria.rossi@example.com", "password")

# TC-8
@patch("participium.services.auth_service.verify_password")
def test_authenticate_unverified_username_unsuccess(mock_verify_password, auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = PENDING_VERIFICATION_USER
    mock_verify_password.return_value = True

    with pytest.raises(AuthenticationError, match="Email verification is required before login."):
        service.authenticate("maria.rossi", "password")


# TC-9
def test_authenticate_unactive_username_unsuccess(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = UNACTIVE_VERIFIED_USER

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("giulia.neri", "password")

# TC-10
def test_authenticate_unactive_email_unsuccess(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    auth_service_bundle["user_repository"].get_by_username_or_email.return_value = UNACTIVE_VERIFIED_USER

    with pytest.raises(AuthenticationError, match="Invalid credentials."):
        service.authenticate("giulia.neri@example.com", "password")

# verify_email test cases

# TC-11
def test_verify_email_success(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    token_repo = service.token_repository

    mock_token = Mock()
    mock_token.is_used = False
    mock_token.expires_at = utcnow() + timedelta(hours=1)
    
    mock_token.user = CORRECT_USER 
    
    token_repo.get_by_token.return_value = mock_token

    verified_user = service.verify_email("token_valido_123")

    assert isinstance(verified_user, User)
    assert verified_user.username == CORRECT_USER.username
    assert mock_token.is_used is True  
    assert mock_token.user.is_email_verified is True 

# TC-12
def test_verify_email_invalid_unsucces(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    token_repo = service.token_repository

    mock_token = Mock()
    mock_token.is_used = True
    mock_token.expires_at = utcnow() + timedelta(hours=1)
    
    mock_token.user = CORRECT_USER 
    
    token_repo.get_by_token.return_value = mock_token

    with pytest.raises(ValidationError):
        service.verify_email("invalid_token")

# TC-13
def test_verify_email_expired_unsucces(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    token_repo = service.token_repository

    mock_token = Mock()
    mock_token.is_used = False
    mock_token.expires_at = utcnow() - timedelta(hours=1)
    
    mock_token.user = CORRECT_USER 
    
    token_repo.get_by_token.return_value = mock_token

    with pytest.raises(ValidationError):
        service.verify_email("invalid_token")

# register_user test cases

# TC-14
def test_register_user_missing_field_unsucces(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    token_repo = service.token_repository

    payload = {"username" : "Luca"}

    with pytest.raises(ValidationError):
        service.register_user(payload)


# TC-15
def test_register_user_already_used_username_unsucces(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    user_repo = service.user_repository
    
    payload = {"username" : "luca.bianchi", "first_name" : "Luca", "last_name": "Bianchi", "email": "luca.bianchi@example.com", "password": "12345678"}
    mock_user = Mock(spec = User)
    mock_user.username = "luca.bianchi"
    user_repo.get_by_username.return_value = mock_user
    
    with pytest.raises(ValidationError):
        service.register_user(payload)
    

# TC-16
def test_register_user_already_used_email_unsuccess(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    user_repo = service.user_repository
    
    payload = {"username" : "luca.bianchi", "first_name" : "Luca", "last_name": "Bianchi", "email": "luca.bianchi@example.com", "password": "12345678"}
    mock_user = Mock(spec = User)
    mock_user.username = "LucaBianchi"
    mock_user.email = "luca.bianchi@example.com"
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = mock_user

    with pytest.raises(ValidationError):
        service.register_user(payload)

# TC-17
def test_register_user_success(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    user_repo = service.user_repository
    
    payload = {"username" : "luca.bianchi", "first_name" : "Luca", "last_name": "Bianchi", "email": "luca.bianchi@example.com", "password": "12345678"}
    mock_user = Mock(spec = User)
    mock_user.username = "LucaBianchi"
    mock_user.email = "luca.bianchi@example.com"
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None
    mock_token = "TOKEN"
    base_url = "https://example.com"

    result_user, result_verification_url = service.register_user(payload, base_url )

    assert isinstance(result_user, User)
    assert isinstance(result_verification_url, str)

    assert result_user.username == CORRECT_USER.username
    assert result_user.first_name == CORRECT_USER.first_name
    assert result_user.last_name == CORRECT_USER.last_name
    assert result_user.email == CORRECT_USER.email
    
# TC-18
def test_register_user_url_none_success(auth_service_bundle: dict[str, object]) -> None:
    service = auth_service_bundle["service"]
    user_repo = service.user_repository
    
    payload = {"username" : "luca.bianchi", "first_name" : "Luca", "last_name": "Bianchi", "email": "luca.bianchi@example.com", "password": "12345678"}
    mock_user = Mock(spec = User)
    mock_user.username = "LucaBianchi"
    mock_user.email = "luca.bianchi@example.com"
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None
    mock_token = "TOKEN"

    result_user, result_verification_url = service.register_user(payload, None)

    assert isinstance(result_user, User)
    assert result_user.username == CORRECT_USER.username
    assert result_user.first_name == CORRECT_USER.first_name
    assert result_user.last_name == CORRECT_USER.last_name
    assert result_user.email == CORRECT_USER.email
    assert result_verification_url is None



    


    
