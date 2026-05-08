from __future__ import annotations
from participium.services.auth_service import AuthService
import pytest
from participium.core.exceptions import AuthenticationError
from participium.models.user import User
from participium.services.auth_service import AuthService

# Function: authenticate
# Inputs: identifier (str), password (str)
# Expected Output:
# - The authenticated `User` if credentials are valid, the matched user is active, and email is verified.
# - AuthenticationError: if credentials are invalid.
# - AuthenticationError: if the matched user exists but is inactive.
# - AuthenticationError: if the matched user exists but email is not verified.
#def authenticate(identifier: str, password: str) -> User


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

#TC-1
def test_authenticate_empty_identifier_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = ""
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)

#TC-2
def test_authenticate_empty_password_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "luca.bianchi"
    password_value = ""

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)
    
#TC-3
def test_authenticate_wrong_identifier_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "pippo"
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)

#TC-4
def test_authenticate_wrong_password_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "luca.bianchi"
    password_value = "psw"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)

#TC-5
def test_authenticate_username_success(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "luca.bianchi"
    password_value = "password"

    verified_user = auth_service.authenticate(identifier_value, password_value)

    assert isinstance(verified_user, User)
    assert verified_user.id == CORRECT_USER.id
    assert verified_user.username == CORRECT_USER.username
    assert verified_user.first_name == CORRECT_USER.first_name
    assert verified_user.last_name == CORRECT_USER.last_name
    assert verified_user.email == CORRECT_USER.email
    assert verified_user.is_email_verified is True

#TC-6
def test_authenticate_email_success(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "luca.bianchi@example.com"
    password_value = "password"

    verified_user = auth_service.authenticate(identifier_value, password_value)

    assert isinstance(verified_user, User)
    assert verified_user.id == CORRECT_USER.id
    assert verified_user.username == CORRECT_USER.username
    assert verified_user.first_name == CORRECT_USER.first_name
    assert verified_user.last_name == CORRECT_USER.last_name
    assert verified_user.email == CORRECT_USER.email
    assert verified_user.is_email_verified is True

#TC-7
def test_authenticate_unverified_email_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "maria.rossi@example.com"
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)

#TC-8
def test_authenticate_unverified_username_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "maria.rossi"
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)


#TC-9
def test_authenticate_unactive_username_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "giulia.neri"
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)

#TC-10
def test_authenticate_unactive_email_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "giulia.neri@example.com"
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)