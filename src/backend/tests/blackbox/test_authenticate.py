from __future__ import annotations

from participium.services.auth_service import AuthService

# Function: authenticate
# Inputs: identifier (str), password (str)
# Expected Output:
# - The authenticated `User` if credentials are valid, the matched user is active, and email is verified.
# - AuthenticationError: if credentials are invalid.
# - AuthenticationError: if the matched user exists but is inactive.
# - AuthenticationError: if the matched user exists but email is not verified.
#def authenticate(identifier: str, password: str) -> User
#| TC-ID | identifier | password | Input |Expected | Fixture |
#| :---- | :--------- | :------- | :---- |:------- | :------ |
#|  TC-1 | empty | * | ("","psw19") | AuthenticationError("credentials are invalid") | * |
#|  TC-2 | * | empty | ("Group19","") | AuthenticationError("credentials are invalid") | * |
#|  TC-3 | any | * | ("Group19","psw19") | AuthenticationError("credentials are invalid")| * |
#|  TC-4 | * | any | ("Group20","psw19") | AuthenticationError("credentials are invalid") | * |
#|  TC-5 | correct username | correct | ("Group20","psw20") | The authenticated `User` | Active and Verified |
#|  TC-6 | correct and verified email | correct | ("Group20@gmail.com","psw20") | The authenticated `User` | Active and Verified |
#|  TC-7 | correct email | correct | ("Group20@gmail.com","psw20") | AuthenticationError("the matched user exists but email is not verified") | Active and not Verified email |
#|  TC-8 | correct username | correct | ("Group20","psw20") | AuthenticationError("the matched user exists but email is not verified") | Active and not Verified email |
#|  TC-9 | correct username | correct | ("Group20","psw20") | AuthenticationError("the matched user exists but is inactive") | Inactive |
#|  TC-10 | correct email | correct | ("Group20@gmail.com","psw20") | AuthenticationError("the matched user exists but is inactive") | Inactive |
# equivalence classes for 


PENDING_VERIFICATION_USER = User(
    id=101,
    username="Group20",
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

def test_authenticate_username_success(seed_verify_email_data: None) -> None:
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

def test_authenticate_email_success(seed_verify_email_data: None) -> None:
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

def test_authenticate_username_unsuccess(seed_authenticate_data: None) -> None:
    auth_service = AuthService()
    identifier_value = "pippo"
    password_value = "password"

    with pytest.raises(AuthenticationError):
        auth_service.authenticate(identifier_value, password_value)
