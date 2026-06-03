from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

from participium.app import create_app
from participium.core.security import hash_password
from participium.database import close_connection, get_session
from participium.models.category import Category
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.models.notification import Notification, NotificationType


pytestmark = pytest.mark.e2e

PASSWORD = "Password1!"


@pytest.fixture
def app(monkeypatch):
    """
    Creates a real Flask application backed by an in-memory SQLite database.

    Each factory fixture uses its own short-lived app-context block so that
    committed data is safely in SQLite before any test-client request is made,
    avoiding SQLAlchemy scoped-session conflicts between setup and request
    teardown hooks.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AUTO_INIT_DB", "true")
    monkeypatch.setenv("BOOTSTRAP_REFERENCE_DATA", "false")
    monkeypatch.setenv("BOOTSTRAP_DEMO_DATA", "false")
    monkeypatch.setenv("EXPOSE_VERIFICATION_LINKS", "true")

    with patch("participium.gateways.email_gateway.EmailGateway.send", return_value=None):
        application = create_app()
        application.config["TESTING"] = True
        try:
            application.config["SETTINGS"].expose_verification_links = True
        except AttributeError:
            pass

        yield application

    close_connection()


@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def make_category(app):
    _counter = [0]

    def factory(*, name: str | None = None, is_active: bool = True) -> SimpleNamespace:
        _counter[0] += 1
        with app.app_context():
            session = get_session()
            cat = Category(name=name or f"Category {_counter[0]}", is_active=is_active)
            session.add(cat)
            session.commit()
            session.refresh(cat)
            return SimpleNamespace(id=cat.id, name=cat.name, is_active=cat.is_active)

    return factory


@pytest.fixture
def make_notification(app):
    def factory(*, user_id: int) -> SimpleNamespace:
        with app.app_context():
            session = get_session()
            notif = Notification(
                user_id=user_id,
                type=NotificationType.STATUS_CHANGE,  
                title="Test notification",
                body="Test body",
                is_read=False,
            )
            session.add(notif)
            session.commit()
            session.refresh(notif)
            return SimpleNamespace(id=notif.id, user_id=notif.user_id)
    return factory

@pytest.fixture
def make_user(app):
    _counter = [0]

    def factory(
        *,
        username: str | None = None,
        email: str | None = None,
        role: Role = Role.CITIZEN,
        password: str = PASSWORD,
        category_id: int | None = None,
        is_active: bool = True,
        is_email_verified: bool = True,
    ) -> SimpleNamespace:
        _counter[0] += 1
        n = _counter[0]
        with app.app_context():
            session = get_session()
            user = User(
                username=username or f"user_{n}",
                first_name="Test",
                last_name="User",
                email=email or f"user{n}@example.com",
                password_hash=hash_password(password),
                role=role,
                category_id=category_id,
                is_active=is_active,
                is_email_verified=is_email_verified,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return SimpleNamespace(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                category_id=user.category_id,
                is_active=user.is_active,
            )

    return factory


@pytest.fixture
def make_report(app):
    _counter = [0]

    def factory(
        *,
        title: str | None = None,
        reporter_id: int | None = None,
        category_id: int,
        status: ReportStatus = ReportStatus.PENDING_APPROVAL,
        is_anonymous: bool = False,
    ) -> SimpleNamespace:
        _counter[0] += 1
        n = _counter[0]
        with app.app_context():
            session = get_session()
            report = Report(
                title=title or f"Report {n}",
                description="A test description",
                latitude=45.0 + n * 0.01,
                longitude=9.0 + n * 0.01,
                is_anonymous=is_anonymous,
                status=status,
                reporter_id=reporter_id,
                category_id=category_id,
            )
            session.add(report)
            session.commit()
            session.refresh(report)
            return SimpleNamespace(
                id=report.id,
                title=report.title,
                status=report.status,
                reporter_id=report.reporter_id,
                category_id=report.category_id,
                is_anonymous=report.is_anonymous,
            )

    return factory



def api_login(client: FlaskClient, identifier: str, password: str = PASSWORD) -> None:
    """Log in via the API; the test client stores the session cookie."""
    client.post("/api/v1/auth/login", json={"identifier": identifier, "password": password})



@pytest.fixture
def citizen(make_user) -> SimpleNamespace:
    return make_user(role=Role.CITIZEN, username="citizen", email="citizen@example.com")


@pytest.fixture
def operator_category(make_category) -> SimpleNamespace:
    """The category the operator fixture is assigned to."""
    return make_category(name="Op Category")


@pytest.fixture
def operator_user(make_user, operator_category) -> SimpleNamespace:
    return make_user(
        role=Role.OPERATOR,
        username="operator",
        email="operator@example.com",
        category_id=operator_category.id,
    )


@pytest.fixture
def admin_user(make_user) -> SimpleNamespace:
    return make_user(role=Role.ADMIN, username="admin", email="admin@example.com")


@pytest.fixture
def citizen_client(client, citizen) -> FlaskClient:
    api_login(client, "citizen")
    return client


@pytest.fixture
def operator_client(client, operator_user) -> FlaskClient:
    api_login(client, "operator")
    return client


@pytest.fixture
def admin_client(client, admin_user) -> FlaskClient:
    api_login(client, "admin")
    return client