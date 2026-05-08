from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import ValidationError
from participium.models.enums import Role
from participium.models.user import User
from participium.services.user_service import UserService

pytestmark = pytest.mark.whitebox


def _user(*, user_id: int, username: str, email: str, role: Role = Role.CITIZEN) -> User:
    return User(
        id=user_id,
        username=username,
        email=email,
        role=role,
        is_active=True,
        first_name="Original",
        last_name="User",
        email_notifications_enabled=True,
    )


@pytest.fixture
def user_service_bundle() -> dict[str, object]:
    session = Mock()
    user_repository = Mock()

    user_repository.get_by_username.return_value = False
    user_repository.get_by_email.return_value = False
    
    service = UserService(
        session=session,
        user_repository=user_repository
    )
    
    service.get_user = Mock()
    service._parse_role = Mock()
    service._resolve_operator_category = Mock()
    
    return {
        "service": service,
        "session": session,
        "user_repository": user_repository,
    }

@pytest.fixture
def existing_user_case(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(user_id=102, username="luca.bianchi", email="luca@test.com")
    user_service_bundle["service"].get_user.return_value = user
    user_service_bundle["user"] = user
    return user_service_bundle

# --- TEST CASES ---

def test_update_user_username_conflict(existing_user_case: dict[str, object]) -> None:
    """TC-1a: Errore se lo username è già occupato (Ramo True del primo if)."""
    service = existing_user_case["service"]
    repo = existing_user_case["user_repository"]
    
    repo.get_by_username.return_value = True
    
    payload = {"username": "nuovo.username"}

    with pytest.raises(ValidationError, match="Username already in use."):
        service.update_user(102, payload)


def test_update_user_email_conflict(existing_user_case: dict[str, object]) -> None:
    """TC-1b: Errore se l'email è già occupata (Ramo True del secondo if)."""
    service = existing_user_case["service"]
    repo = existing_user_case["user_repository"]
    
    repo.get_by_username.return_value = False
    repo.get_by_email.return_value = True
    
    payload = {"email": "nuova@email.com"}

    with pytest.raises(ValidationError, match="Email already in use."):
        service.update_user(102, payload)

def test_update_user_full_success(existing_user_case: dict[str, object]) -> None:
    """TC-3: Successo totale. Risolve il tuo errore forzando i mock a False."""
    service = existing_user_case["service"]
    repo = existing_user_case["user_repository"]
    user = existing_user_case["user"]
    
    repo.get_by_username.return_value = False
    repo.get_by_email.return_value = False
    
    service._parse_role.return_value = Role.OPERATOR
    service._resolve_operator_category.return_value = Mock(id=5)

    payload = {
        "username": "nuovo.luca",
        "email": "nuova@email.com",
        "first_name": "  Gianluca  ",
        "role": Role.OPERATOR,
        "category_id": 5,
        "is_active": False,
        "email_notifications_enabled": False
    }

    updated_user = service.update_user(102, payload)

    assert updated_user.username == "nuovo.luca"
    assert updated_user.first_name == "Gianluca"
    assert updated_user.email == "nuova@email.com"
    assert updated_user.role == Role.OPERATOR
    assert updated_user.is_active is False
    existing_user_case["session"].commit.assert_called_once()

def test_update_user_identical_data_and_types(existing_user_case: dict[str, object]) -> None:
    """Copre i rami 'False' delle condizioni 'if username != user.username' e 'isinstance(str)'."""
    service = existing_user_case["service"]
    user = existing_user_case["user"]
    repo = existing_user_case["user_repository"]

    payload = {
        "username": user.username, 
        "email": user.email,
        "last_name": 999 
    }

    service.update_user(102, payload)
    
    repo.get_by_username.assert_not_called()
    repo.get_by_email.assert_not_called()
    assert user.last_name == 999

def test_update_user_missing_payload_keys(existing_user_case: dict[str, object]) -> None:
    """Copre i rami mancanti (Missing lines 90, 93, 95) quando le chiavi non sono nel payload."""
    service = existing_user_case["service"]
 
    service.update_user(102, {"first_name": "SoloNome"})
    
    assert existing_user_case["user"].first_name == "SoloNome"

