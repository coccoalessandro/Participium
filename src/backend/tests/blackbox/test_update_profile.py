from __future__ import annotations

from participium.services.user_service import UserService
from participium.models.user import User
from participium.models.enums import Role
from participium.core.exceptions import ValidationError

import pytest

# Function: 
# Inputs: user(User), username(str | None), first_name(str | None), last_name(str | None), email_notifications_enabled(bool | None), profile_picture(FileStorage | None))
# Expected Output:
# - The updated `User` if the update is successful.
# - ValidationError if the `username` is already used by another account.
#def update_profile(
#        self,
#        user: User,
#        username: str | None = None,
#        first_name: str | None = None,
#        last_name: str | None = None,
#        email_notifications_enabled: bool | None = None,
#        profile_picture: FileStorage | None = None,
#    ) -> User

CORRECT_USER = User(
    id=102,
    username="luca.bianchi",
    first_name="Luca",
    last_name="Bianchi",
    email="luca.bianchi@example.com",
    password_hash="HASHED_PASSWORD_102",
    is_active=True,
    is_email_verified=True,
    email_notifications_enabled=True,
    role=Role.CITIZEN
)

CORRECT_USER_USED_USERNAME = User(
    id=103,
    username="anna.gialli",
    first_name="Anna",
    last_name="Gialli",
    email="Anna.Gialli@example.com",
    password_hash="HASHED_PASSWORD_103",
    is_active=True,
    is_email_verified=True,
    email_notifications_enabled=True,
    role=Role.CITIZEN
)

# TC-1
def test_update_profile_success(seed_update_profile_data: None) -> None:
    user_service = UserService()
    username = "bianchi.luca"

    result = user_service.update_profile(CORRECT_USER, username, CORRECT_USER.first_name, CORRECT_USER.last_name, CORRECT_USER.email_notifications_enabled, None)
    
    assert isinstance(result, User)
    assert result.username == username
    assert result.first_name == CORRECT_USER.first_name
    assert result.last_name == CORRECT_USER.last_name
    assert result.email_notifications_enabled == CORRECT_USER.email_notifications_enabled

# TC-2
def test_update_profile_unchanged(seed_update_profile_data: None) -> None:
    user_service = UserService()
    
    result = user_service.update_profile(CORRECT_USER, CORRECT_USER.username, CORRECT_USER.first_name, CORRECT_USER.last_name, CORRECT_USER.email_notifications_enabled, None)
    
    assert isinstance(result, User)
    assert result == CORRECT_USER

# TC-3
def test_update_profile_unsucess_already_used(seed_update_profile_data: None) -> None:
    user_service = UserService()
    used_username = "anna.gialli"
    
    with pytest.raises(ValidationError):
        user_service.update_profile(CORRECT_USER, used_username, CORRECT_USER.first_name, CORRECT_USER.last_name, CORRECT_USER.email_notifications_enabled, None)
    