from __future__ import annotations

import pytest

from participium.models.enums import Role
from participium.repositories.user_repository import UserRepository
from participium.models.user import User
from participium.models.enums import Role
from participium.repositories.user_repository import UserRepository

pytestmark = pytest.mark.integration




def test_add_persists_user_and_get_by_id_retrieves_it(db_session, make_user):
    user = make_user(username="mario_rossi", email="mario@example.com")
    db_session.commit()

    repo = UserRepository(db_session)
    result = repo.get_by_id(user.id)

    assert result is not None
    assert result.username == "mario_rossi"
    assert result.email == "mario@example.com"


def test_get_by_id_returns_none_when_user_does_not_exist(db_session):
    repo = UserRepository(db_session)

    assert repo.get_by_id(9999) is None


def test_get_by_id_loads_category_relationship(db_session, make_category, make_user):
    cat = make_category(name="Waste")
    user = make_user(role=Role.OPERATOR, category_id=cat.id)
    db_session.commit()

    repo = UserRepository(db_session)
    result = repo.get_by_id(user.id)

    assert result.category is not None
    assert result.category.name == "Waste"



def test_get_by_email_returns_matching_user(db_session, make_user):
    make_user(username="luigi", email="luigi@example.com")
    db_session.commit()

    repo = UserRepository(db_session)
    result = repo.get_by_email("luigi@example.com")

    assert result is not None
    assert result.username == "luigi"


def test_get_by_email_returns_none_when_not_found(db_session):
    repo = UserRepository(db_session)

    assert repo.get_by_email("missing@example.com") is None



def test_get_by_username_returns_matching_user(db_session, make_user):
    make_user(username="anna_bianchi")
    db_session.commit()

    repo = UserRepository(db_session)
    result = repo.get_by_username("anna_bianchi")

    assert result is not None
    assert result.username == "anna_bianchi"


def test_get_by_username_returns_none_when_not_found(db_session):
    repo = UserRepository(db_session)

    assert repo.get_by_username("ghost_user") is None



def test_get_by_username_or_email_matches_on_username(db_session, make_user):
    make_user(username="find_me", email="findme@example.com")
    db_session.commit()

    repo = UserRepository(db_session)
    result = repo.get_by_username_or_email("find_me")

    assert result is not None
    assert result.username == "find_me"


def test_get_by_username_or_email_matches_on_email(db_session, make_user):
    make_user(username="find_me", email="findme@example.com")
    db_session.commit()

    repo = UserRepository(db_session)
    result = repo.get_by_username_or_email("findme@example.com")

    assert result is not None
    assert result.email == "findme@example.com"


def test_get_by_username_or_email_returns_none_when_no_match(db_session):
    repo = UserRepository(db_session)

    assert repo.get_by_username_or_email("nobody") is None




def test_list_all_returns_all_users(db_session, make_user):
    make_user(username="user_a")
    make_user(username="user_b")
    make_user(username="user_c")
    db_session.commit()

    repo = UserRepository(db_session)
    results = repo.list_all()

    usernames = {u.username for u in results}
    assert {"user_a", "user_b", "user_c"} <= usernames


def test_list_all_returns_empty_when_no_users(db_session):
    repo = UserRepository(db_session)

    assert repo.list_all() == []



def test_delete_removes_user_from_database(db_session, make_user):
    user = make_user(username="to_delete")
    db_session.commit()

    repo = UserRepository(db_session)
    repo.delete(user)
    db_session.commit()

    assert repo.get_by_id(user.id) is None


def test_delete_does_not_affect_other_users(db_session, make_user):
    user_a = make_user(username="keep_me")
    user_b = make_user(username="delete_me")
    db_session.commit()

    repo = UserRepository(db_session)
    repo.delete(user_b)
    db_session.commit()

    assert repo.get_by_id(user_a.id) is not None
    assert repo.get_by_id(user_b.id) is None


def test_add_persists_user_via_repository(db_session):

    repo = UserRepository(db_session)
    user = User(
        username="direct_user",
        first_name="Test",
        last_name="User",
        email="direct@example.com",
        password_hash="hashed_pw",
        role=Role.CITIZEN,
        is_active=True,
        is_email_verified=True,
    )
    returned = repo.add(user)
    db_session.commit()

    assert returned is user
    assert user.id is not None