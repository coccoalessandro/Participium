from __future__ import annotations

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.category import Category
from participium.models.enums import NotificationType, Role, ReportStatus
from participium.models.message import Message
from participium.models.notification import Notification
from participium.models.report import Report, ReportFollower, ReportPhoto, ReportStatusHistory
from participium.models.token import EmailVerificationToken
from participium.models.user import User


@pytest.fixture
def db_session(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    open_connection()
    create_all()
    session = get_session()
    yield session
    close_connection()


@pytest.fixture
def make_category(db_session):
    def factory(*, name: str = "Test Category", is_active: bool = True) -> Category:
        cat = Category(name=name, is_active=is_active)
        db_session.add(cat)
        db_session.flush()
        return cat

    return factory


@pytest.fixture
def make_user(db_session):
    _counter = [0]

    def factory(
        *,
        username: str | None = None,
        email: str | None = None,
        role: Role = Role.CITIZEN,
        category_id: int | None = None,
        is_active: bool = True,
        is_email_verified: bool = True,
    ) -> User:
        _counter[0] += 1
        n = _counter[0]
        user = User(
            username=username or f"user_{n}",
            first_name="Test",
            last_name="User",
            email=email or f"user{n}@example.com",
            password_hash="hashed_pw",
            role=role,
            category_id=category_id,
            is_active=is_active,
            is_email_verified=is_email_verified,
        )
        db_session.add(user)
        db_session.flush()
        return user

    return factory


@pytest.fixture
def make_report(db_session):
    _counter = [0]

    def factory(
        *,
        title: str | None = None,
        reporter_id: int | None = None,
        category_id: int,
        status: ReportStatus = ReportStatus.PENDING_APPROVAL,
        is_anonymous: bool = False,
    ) -> Report:
        _counter[0] += 1
        n = _counter[0]
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
        db_session.add(report)
        db_session.flush()
        return report

    return factory


@pytest.fixture
def make_notification(db_session):
    def factory(
        user_id,
        report_id,
        notification_type=NotificationType.MESSAGE,
        title="Test notification",
        body="Test body",          
        is_read=False,
    ):
        notif = Notification(
            user_id=user_id,
            report_id=report_id,
            type=notification_type,
            title=title,
            body=body,             
            is_read=is_read,
        )
        db_session.add(notif)
        db_session.flush()         
        return notif
    return factory

@pytest.fixture
def make_message(db_session):
    def factory(
        *,
        report_id: int,
        sender_id: int | None = None,
        recipient_id: int | None = None,
        body: str = "Hello",
    ) -> Message:
        message = Message(
            report_id=report_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            body=body,
        )
        db_session.add(message)
        db_session.flush()
        return message

    return factory


from datetime import datetime, timedelta, timezone

@pytest.fixture
def make_token(db_session):
    def factory(user_id, token="test-token", expires_at=None):
        from participium.models.token import EmailVerificationToken
        tok = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at or datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db_session.add(tok)
        return tok
    return factory


@pytest.fixture
def make_status_entry(db_session):
    def factory(
        *,
        report_id: int,
        previous_status: ReportStatus | None = None,
        new_status: ReportStatus = ReportStatus.PENDING_APPROVAL,
        changed_by_id: int | None = None,
        note: str | None = None,
    ) -> ReportStatusHistory:
        entry = ReportStatusHistory(
            report_id=report_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by_id=changed_by_id,
            note=note,
        )
        db_session.add(entry)
        db_session.flush()
        return entry

    return factory