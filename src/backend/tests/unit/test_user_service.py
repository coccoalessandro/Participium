from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import NotFoundError, ValidationError
from participium.models.enums import Role
from participium.models.user import User
from participium.services.user_service import UserService


def _user(
    *,
    user_id: int = 1,
    username: str = "mario_rossi",
    first_name: str = "Mario",
    last_name: str = "Rossi",
    email: str = "mario@example.com",
    role: Role = Role.CITIZEN,
    category_id: int | None = None,
    is_active: bool = True,
    is_email_verified: bool = True,
    email_notifications_enabled: bool = True,
    profile_picture_path: str | None = None,
) -> User:
    user = User(
        id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash="hashed",
        role=role,
        category_id=category_id,
        is_active=is_active,
        is_email_verified=is_email_verified,
        email_notifications_enabled=email_notifications_enabled,
    )
    user.profile_picture_path = profile_picture_path
    return user


def _category(*, category_id: int = 1, is_active: bool = True) -> Mock:
    cat = Mock()
    cat.id = category_id
    cat.is_active = is_active
    return cat



@pytest.fixture
def user_service_bundle() -> dict[str, object]:
    session = Mock()
    user_repository = Mock()
    category_repository = Mock()
    token_repository = Mock()
    notification_repository = Mock()
    storage_service = Mock()

    service = UserService(
        session=session,
        user_repository=user_repository,
        category_repository=category_repository,
        token_repository=token_repository,
        notification_repository=notification_repository,
        storage_service=storage_service,
    )

    return {
        "service": service,
        "session": session,
        "user_repository": user_repository,
        "category_repository": category_repository,
        "token_repository": token_repository,
        "notification_repository": notification_repository,
        "storage_service": storage_service,
    }



@pytest.fixture
def update_profile_base(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user()
    user_service_bundle["user_repository"].get_by_username.return_value = None
    user_service_bundle["user"] = user
    return user_service_bundle


@pytest.fixture
def update_profile_duplicate_username(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user()
    other_user = _user(user_id=99, username="taken")
    user_service_bundle["user_repository"].get_by_username.return_value = other_user
    user_service_bundle["user"] = user
    return user_service_bundle


@pytest.fixture
def update_profile_with_picture(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user()
    user_service_bundle["user_repository"].get_by_username.return_value = None
    user_service_bundle["storage_service"].save.return_value = "uuid_photo.jpg"
    uploaded_file = Mock()
    uploaded_file.filename = "photo.jpg"
    user_service_bundle["user"] = user
    user_service_bundle["uploaded_file"] = uploaded_file
    return user_service_bundle


def test_update_profile_raises_if_username_already_in_use(
    update_profile_duplicate_username: dict[str, object],
) -> None:
    service = update_profile_duplicate_username["service"]
    user = update_profile_duplicate_username["user"]

    with pytest.raises(ValidationError, match="Username already in use."):
        service.update_profile(user, username="taken")


def test_update_profile_does_not_raise_if_username_is_unchanged(
    update_profile_base: dict[str, object],
) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]
    original_username = user.username

    result = service.update_profile(user, username=original_username)

    assert result.username == original_username


def test_update_profile_updates_username(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]

    service.update_profile(user, username="luigi_verdi")

    assert user.username == "luigi_verdi"


def test_update_profile_strips_whitespace_from_username(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]

    service.update_profile(user, username="  luigi_verdi  ")

    assert user.username == "luigi_verdi"


def test_update_profile_updates_first_name(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]

    service.update_profile(user, first_name="Luigi")

    assert user.first_name == "Luigi"


def test_update_profile_updates_last_name(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]

    service.update_profile(user, last_name="Verdi")

    assert user.last_name == "Verdi"


def test_update_profile_updates_email_notifications_enabled(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]

    service.update_profile(user, email_notifications_enabled=False)

    assert user.email_notifications_enabled is False


def test_update_profile_saves_picture_and_stores_path(
    update_profile_with_picture: dict[str, object],
) -> None:
    service = update_profile_with_picture["service"]
    user = update_profile_with_picture["user"]
    uploaded_file = update_profile_with_picture["uploaded_file"]
    storage_service = update_profile_with_picture["storage_service"]

    service.update_profile(user, profile_picture=uploaded_file)

    storage_service.save.assert_called_once_with(uploaded_file)
    assert user.profile_picture_path == "uuid_photo.jpg"


def test_update_profile_does_not_save_picture_when_filename_is_empty(
    update_profile_base: dict[str, object],
) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]
    storage_service = update_profile_base["storage_service"]
    no_name_file = Mock()
    no_name_file.filename = ""

    service.update_profile(user, profile_picture=no_name_file)

    storage_service.save.assert_not_called()


def test_update_profile_commits_session(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    session = update_profile_base["session"]
    user = update_profile_base["user"]

    service.update_profile(user, first_name="Luigi")

    session.commit.assert_called_once_with()


def test_update_profile_returns_updated_user(update_profile_base: dict[str, object]) -> None:
    service = update_profile_base["service"]
    user = update_profile_base["user"]

    result = service.update_profile(user, first_name="Luigi")

    assert result is user



@pytest.fixture
def get_user_found(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(user_id=5)
    user_service_bundle["user_repository"].get_by_id.return_value = user
    user_service_bundle["user"] = user
    return user_service_bundle


@pytest.fixture
def get_user_not_found(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user_service_bundle["user_repository"].get_by_id.return_value = None
    return user_service_bundle



def test_get_user_returns_user_when_found(get_user_found: dict[str, object]) -> None:
    service = get_user_found["service"]
    user = get_user_found["user"]

    result = service.get_user(user_id=5)

    assert result is user


def test_get_user_raises_not_found_when_missing(get_user_not_found: dict[str, object]) -> None:
    service = get_user_not_found["service"]

    with pytest.raises(NotFoundError):
        service.get_user(user_id=999)


def test_get_user_calls_repository_with_correct_id(get_user_found: dict[str, object]) -> None:
    service = get_user_found["service"]
    user_repository = get_user_found["user_repository"]

    service.get_user(user_id=5)

    user_repository.get_by_id.assert_called_once_with(5)



def test_list_users_delegates_to_repository(user_service_bundle: dict[str, object]) -> None:
    service = user_service_bundle["service"]
    user_repository = user_service_bundle["user_repository"]
    users = [_user(user_id=1), _user(user_id=2)]
    user_repository.list_all.return_value = users

    result = service.list_users()

    assert result == users
    user_repository.list_all.assert_called_once_with()



@pytest.fixture
def create_user_base(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user_service_bundle["user_repository"].get_by_username.return_value = None
    user_service_bundle["user_repository"].get_by_email.return_value = None
    user_service_bundle["payload"] = {
        "username": "luigi_verdi",
        "first_name": "Luigi",
        "last_name": "Verdi",
        "email": "luigi@example.com",
        "password": "secret123",
        "role": Role.CITIZEN.value,
    }
    return user_service_bundle


@pytest.fixture
def create_operator_bundle(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user_service_bundle["user_repository"].get_by_username.return_value = None
    user_service_bundle["user_repository"].get_by_email.return_value = None
    category = _category(category_id=3)
    user_service_bundle["category_repository"].get_by_id.return_value = category
    user_service_bundle["payload"] = {
        "username": "op_user",
        "first_name": "Op",
        "last_name": "User",
        "email": "op@example.com",
        "password": "secret123",
        "role": Role.OPERATOR.value,
        "category_id": 3,
    }
    return user_service_bundle



def test_create_user_raises_if_required_field_missing(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]
    payload = dict(create_user_base["payload"])
    del payload["username"]

    with pytest.raises(ValidationError, match="Missing required fields"):
        service.create_user(payload)


def test_create_user_raises_if_username_already_in_use(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]
    create_user_base["user_repository"].get_by_username.return_value = _user()

    with pytest.raises(ValidationError, match="Username already in use."):
        service.create_user(create_user_base["payload"])


def test_create_user_raises_if_email_already_in_use(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]
    create_user_base["user_repository"].get_by_email.return_value = _user()

    with pytest.raises(ValidationError, match="Email already in use."):
        service.create_user(create_user_base["payload"])


def test_create_user_raises_for_invalid_role(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]
    payload = dict(create_user_base["payload"])
    payload["role"] = "nonexistent_role"

    with pytest.raises(ValidationError):
        service.create_user(payload)


def test_create_user_adds_to_repository_and_commits(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]
    user_repository = create_user_base["user_repository"]
    session = create_user_base["session"]

    service.create_user(create_user_base["payload"])

    user_repository.add.assert_called_once()
    session.commit.assert_called_once_with()


def test_create_user_returns_user_with_correct_fields(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]

    result = service.create_user(create_user_base["payload"])

    assert result.username == "luigi_verdi"
    assert result.first_name == "Luigi"
    assert result.last_name == "Verdi"
    assert result.email == "luigi@example.com"
    assert result.role == Role.CITIZEN


def test_create_user_stores_email_lowercased(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]
    payload = dict(create_user_base["payload"])
    payload["email"] = "Luigi@Example.COM"

    result = service.create_user(payload)

    assert result.email == "luigi@example.com"


def test_create_user_sets_is_email_verified_to_true(create_user_base: dict[str, object]) -> None:
    service = create_user_base["service"]

    result = service.create_user(create_user_base["payload"])

    assert result.is_email_verified is True


def test_create_operator_resolves_category(create_operator_bundle: dict[str, object]) -> None:
    service = create_operator_bundle["service"]

    result = service.create_user(create_operator_bundle["payload"])

    assert result.category_id == 3


def test_create_operator_raises_if_category_is_missing(create_operator_bundle: dict[str, object]) -> None:
    service = create_operator_bundle["service"]
    payload = dict(create_operator_bundle["payload"])
    del payload["category_id"]

    with pytest.raises(ValidationError):
        service.create_user(payload)



@pytest.fixture
def update_user_base(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(user_id=10, username="mario_rossi", email="mario@example.com", role=Role.CITIZEN)
    user_service_bundle["user_repository"].get_by_id.return_value = user
    user_service_bundle["user_repository"].get_by_username.return_value = None
    user_service_bundle["user_repository"].get_by_email.return_value = None
    user_service_bundle["user"] = user
    user_service_bundle["payload"] = {"role": Role.CITIZEN.value}
    return user_service_bundle



def test_update_user_raises_if_username_taken(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    update_user_base["user_repository"].get_by_username.return_value = _user(user_id=99, username="new_name")

    with pytest.raises(ValidationError, match="Username already in use."):
        service.update_user(user_id=10, payload={"username": "new_name", "role": Role.CITIZEN.value})


def test_update_user_raises_if_email_taken(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    update_user_base["user_repository"].get_by_email.return_value = _user(user_id=99, email="other@example.com")

    with pytest.raises(ValidationError, match="Email already in use."):
        service.update_user(user_id=10, payload={"email": "other@example.com", "role": Role.CITIZEN.value})


def test_update_user_raises_not_found_if_user_missing(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    update_user_base["user_repository"].get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.update_user(user_id=999, payload={"role": Role.CITIZEN.value})


def test_update_user_raises_for_invalid_role(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]

    with pytest.raises(ValidationError):
        service.update_user(user_id=10, payload={"role": "invalid_role"})


def test_update_user_does_not_raise_if_username_unchanged(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    service.update_user(user_id=10, payload={"username": user.username, "role": Role.CITIZEN.value})


def test_update_user_updates_username(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    service.update_user(user_id=10, payload={"username": "new_mario", "role": Role.CITIZEN.value})

    assert user.username == "new_mario"


def test_update_user_updates_is_active(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    service.update_user(user_id=10, payload={"is_active": False, "role": Role.CITIZEN.value})

    assert user.is_active is False


def test_update_user_updates_email_notifications_enabled(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    service.update_user(user_id=10, payload={"email_notifications_enabled": False, "role": Role.CITIZEN.value})

    assert user.email_notifications_enabled is False


def test_update_user_commits_session(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    session = update_user_base["session"]

    service.update_user(user_id=10, payload=update_user_base["payload"])

    session.commit.assert_called_once_with()


def test_update_user_returns_updated_user(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    result = service.update_user(user_id=10, payload=update_user_base["payload"])

    assert result is user


def test_update_user_sets_non_string_field_without_stripping(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    service.update_user(user_id=10, payload={"last_name": 999, "role": Role.CITIZEN.value})

    assert user.last_name == 999


def test_update_user_without_role_in_payload_uses_current_role(update_user_base: dict[str, object]) -> None:
    service = update_user_base["service"]
    user = update_user_base["user"]

    service.update_user(user_id=10, payload={"first_name": "SoloNome"})

    assert user.first_name == "SoloNome"
    assert user.role == Role.CITIZEN



@pytest.mark.parametrize("role_value", [r.value for r in Role])
def test_parse_role_returns_correct_role_for_valid_value(role_value: str) -> None:
    result = UserService._parse_role(role_value)

    assert isinstance(result, Role)
    assert result.value == role_value


def test_parse_role_raises_for_invalid_value() -> None:
    with pytest.raises(ValidationError):
        UserService._parse_role("nonexistent_role")


@pytest.fixture
def resolve_category_bundle(user_service_bundle: dict[str, object]) -> dict[str, object]:
    return user_service_bundle



def test_resolve_operator_category_returns_none_for_citizen(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]

    assert service._resolve_operator_category(Role.CITIZEN, category_id_value=None) is None


def test_resolve_operator_category_returns_none_for_admin(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]

    assert service._resolve_operator_category(Role.ADMIN, category_id_value=5) is None


def test_resolve_operator_category_raises_if_category_id_is_none(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]

    with pytest.raises(ValidationError):
        service._resolve_operator_category(Role.OPERATOR, category_id_value=None)


def test_resolve_operator_category_raises_if_category_id_is_empty_string(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]

    with pytest.raises(ValidationError):
        service._resolve_operator_category(Role.OPERATOR, category_id_value="")


def test_resolve_operator_category_raises_if_category_id_is_not_numeric(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]

    with pytest.raises(ValidationError):
        service._resolve_operator_category(Role.OPERATOR, category_id_value="abc")


def test_resolve_operator_category_raises_if_category_not_found(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]
    resolve_category_bundle["category_repository"].get_by_id.return_value = None

    with pytest.raises(ValidationError):
        service._resolve_operator_category(Role.OPERATOR, category_id_value=99)


def test_resolve_operator_category_raises_if_category_is_inactive(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]
    resolve_category_bundle["category_repository"].get_by_id.return_value = _category(category_id=7, is_active=False)

    with pytest.raises(ValidationError):
        service._resolve_operator_category(Role.OPERATOR, category_id_value=7)


def test_resolve_operator_category_returns_active_category(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]
    active_category = _category(category_id=3, is_active=True)
    resolve_category_bundle["category_repository"].get_by_id.return_value = active_category

    result = service._resolve_operator_category(Role.OPERATOR, category_id_value=3)

    assert result is active_category


def test_resolve_operator_category_queries_repository_with_correct_id(
    resolve_category_bundle: dict[str, object],
) -> None:
    service = resolve_category_bundle["service"]
    active_category = _category(category_id=3, is_active=True)
    category_repository = resolve_category_bundle["category_repository"]
    category_repository.get_by_id.return_value = active_category

    service._resolve_operator_category(Role.OPERATOR, category_id_value="3")

    category_repository.get_by_id.assert_called_once_with(3)



def _scalars_side_effect(*iterables):
    return [iter(it) for it in iterables]


@pytest.fixture
def delete_account_bundle(user_service_bundle: dict[str, object]) -> dict[str, object]:
    user = _user(user_id=42)
    user_service_bundle["user"] = user
    user_service_bundle["session"].scalars.return_value = iter([])
    user_service_bundle["notification_repository"].list_for_user.return_value = []
    user_service_bundle["token_repository"].list_for_user.return_value = []
    return user_service_bundle



def test_delete_account_deletes_user_via_repository(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    user_repository = delete_account_bundle["user_repository"]

    service.delete_account(user)

    user_repository.delete.assert_called_once_with(user)


def test_delete_account_commits_session(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]

    service.delete_account(user)

    session.commit.assert_called_once_with()


def test_delete_account_queries_notifications_and_tokens_with_correct_user_id(
    delete_account_bundle: dict[str, object],
) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    notification_repository = delete_account_bundle["notification_repository"]
    token_repository = delete_account_bundle["token_repository"]

    service.delete_account(user)

    notification_repository.list_for_user.assert_called_once_with(user.id)
    token_repository.list_for_user.assert_called_once_with(user.id)


def test_delete_account_deletes_each_notification(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    notification_repository = delete_account_bundle["notification_repository"]
    notif_a, notif_b = Mock(), Mock()
    notification_repository.list_for_user.return_value = [notif_a, notif_b]

    service.delete_account(user)

    session.delete.assert_any_call(notif_a)
    session.delete.assert_any_call(notif_b)


def test_delete_account_deletes_each_token(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    token_repository = delete_account_bundle["token_repository"]
    token_a = Mock()
    token_repository.list_for_user.return_value = [token_a]

    service.delete_account(user)

    session.delete.assert_any_call(token_a)


def test_delete_account_anonymises_reports_owned_by_user(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    report = Mock()
    report.reporter_id = user.id
    report.is_anonymous = False
    session.scalars.side_effect = _scalars_side_effect([report], [], [], [])

    service.delete_account(user)

    assert report.reporter_id is None
    assert report.is_anonymous is True


def test_delete_account_deletes_followers_of_user(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    follower = Mock()
    session.scalars.side_effect = _scalars_side_effect([], [follower], [], [])

    service.delete_account(user)

    session.delete.assert_any_call(follower)


def test_delete_account_anonymises_message_sender(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    message = Mock()
    message.sender_id = user.id
    message.recipient_id = 99
    session.scalars.side_effect = _scalars_side_effect([], [], [message], [])

    service.delete_account(user)

    assert message.sender_id is None


def test_delete_account_anonymises_message_recipient(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    message = Mock()
    message.sender_id = 55
    message.recipient_id = user.id
    session.scalars.side_effect = _scalars_side_effect([], [], [message], [])

    service.delete_account(user)

    assert message.recipient_id is None


def test_delete_account_anonymises_message_when_user_is_both_sender_and_recipient(
    delete_account_bundle: dict[str, object],
) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    message = Mock()
    message.sender_id = user.id
    message.recipient_id = user.id
    session.scalars.side_effect = _scalars_side_effect([], [], [message], [])

    service.delete_account(user)

    assert message.sender_id is None
    assert message.recipient_id is None


def test_delete_account_nullifies_status_history_changed_by(delete_account_bundle: dict[str, object]) -> None:
    service = delete_account_bundle["service"]
    user = delete_account_bundle["user"]
    session = delete_account_bundle["session"]
    history = Mock()
    history.changed_by_id = user.id
    session.scalars.side_effect = _scalars_side_effect([], [], [], [history])

    service.delete_account(user)

    assert history.changed_by_id is None