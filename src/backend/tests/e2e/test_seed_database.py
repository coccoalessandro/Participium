from __future__ import annotations

import pytest
from unittest.mock import patch
from participium.app import create_app
from participium.database import close_connection, get_session
from participium.models.category import Category
from participium.models.user import User

pytestmark = pytest.mark.e2e


@pytest.fixture
def seeded_app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AUTO_INIT_DB", "true")
    monkeypatch.setenv("BOOTSTRAP_REFERENCE_DATA", "true")
    monkeypatch.setenv("BOOTSTRAP_DEMO_DATA", "true")

    with patch("participium.gateways.email_gateway.EmailGateway.send", return_value=None):
        application = create_app()
        application.config["TESTING"] = True
        yield application

    close_connection()


def test_seed_reference_data_creates_categories(seeded_app):
    with seeded_app.app_context():
        categories = get_session().query(Category).all()
        assert len(categories) > 0


def test_seed_demo_data_creates_users(seeded_app):
    with seeded_app.app_context():
        users = get_session().query(User).all()
        usernames = [u.username for u in users]
        assert "citizen" in usernames
        assert "operator" in usernames
        assert "admin" in usernames


def test_seed_reference_data_is_idempotent(seeded_app):
    from participium.database.seed import seed_reference_data
    with seeded_app.app_context():
        session = get_session()
        count_before = session.query(Category).count()
        seed_reference_data(session)
        count_after = session.query(Category).count()
        assert count_before == count_after


def test_seed_demo_data_is_idempotent(seeded_app):
    from participium.database.seed import seed_demo_data
    from participium.models.report import Report
    with seeded_app.app_context():
        session = get_session()
        users_before = session.query(User).count()
        reports_before = session.query(Report).count()
        seed_demo_data(session)
        assert session.query(User).count() == users_before
        assert session.query(Report).count() == reports_before