from __future__ import annotations

import pytest

from participium.repositories.token_repository import TokenRepository
from datetime import datetime, timedelta, timezone
from participium.models.token import EmailVerificationToken

pytestmark = pytest.mark.integration



def test_add_persists_token_via_repository(db_session, make_user):
    user = make_user()
    db_session.commit()

    repo = TokenRepository(db_session)
    tok = EmailVerificationToken(
    user_id=user.id,
    token="abc123",
    expires_at=datetime.now(timezone.utc) + timedelta(hours=24), 
    )
    repo.add(tok)
    db_session.commit()

    assert tok.id is not None



def test_get_by_token_returns_matching_token(db_session, make_user, make_token):
    user = make_user()
    token = make_token(user_id=user.id, token="unique_token_xyz")
    db_session.commit()

    repo = TokenRepository(db_session)
    result = repo.get_by_token("unique_token_xyz")

    assert result is not None
    assert result.id == token.id
    assert result.user_id == user.id


def test_get_by_token_returns_none_when_token_does_not_exist(db_session):
    repo = TokenRepository(db_session)

    assert repo.get_by_token("nonexistent_token") is None


def test_get_by_token_returns_none_when_token_belongs_to_different_value(
    db_session, make_user, make_token
):
    user = make_user()
    make_token(user_id=user.id, token="real_token")
    db_session.commit()

    repo = TokenRepository(db_session)
    result = repo.get_by_token("wrong_token")

    assert result is None



def test_list_for_user_returns_all_tokens_for_user(db_session, make_user, make_token):
    user_a = make_user(username="user_a")
    user_b = make_user(username="user_b")
    t1 = make_token(user_id=user_a.id, token="token_a1")
    t2 = make_token(user_id=user_a.id, token="token_a2")
    make_token(user_id=user_b.id, token="token_b1")
    db_session.commit()

    repo = TokenRepository(db_session)
    results = repo.list_for_user(user_a.id)

    ids = {t.id for t in results}
    assert t1.id in ids
    assert t2.id in ids
    assert len(results) == 2


def test_list_for_user_returns_empty_when_user_has_no_tokens(db_session, make_user):
    user = make_user()
    db_session.commit()

    repo = TokenRepository(db_session)
    results = repo.list_for_user(user.id)

    assert results == []


def test_list_for_user_does_not_return_tokens_of_other_users(
    db_session, make_user, make_token
):
    user_a = make_user(username="user_a")
    user_b = make_user(username="user_b")
    make_token(user_id=user_a.id, token="token_a")
    t_b = make_token(user_id=user_b.id, token="token_b")
    db_session.commit()

    repo = TokenRepository(db_session)
    results = repo.list_for_user(user_b.id)

    assert len(results) == 1
    assert results[0].id == t_b.id