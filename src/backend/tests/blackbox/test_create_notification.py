from __future__ import annotations

from participium.services.notification_service import NotificationService

import pytest

from participium.models.user import User
from participium.models.report import Report
from participium.models.enums import NotificationType, ReportStatus, Role
from participium.models.notification import Notification

# Function: 
# Inputs: user (User | None), notification_type (NotificationType), title (str), body (str), report (Report | None)
# Expected Output:
# - A persisted `Notification` for a non-null user, otherwise `None`.
# - Exception: No documented domain exception from the method contract itself.
# - Exception: Email delivery failures, if any, are internally swallowed after logging.
#def create_notification(self, user: User | None, notification_type: NotificationType, title: str, body: str, report: Report | None = None) -> Notification | None


REPORT_WASTE = Report(
    id = 1,
    title = "Waste Report",
    status = ReportStatus.PENDING_APPROVAL,
    rejection_reason = None,
    category_id = 1,
    category = "Waste"
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


#TC-1
def test_create_notification_success_no_report(seed_notification_data: None) -> None:
    notification_service = NotificationService()
    user = CORRECT_USER
    notification_type = NotificationType.STATUS_CHANGED
    title = "Status updated"
    body = "The report status has changed."
    report = None

    result = notification_service.create_notification(user, notification_type, title, body, report)

    assert isinstance(result, Notification)
    assert result.user_id == user.id
    assert result.notification_type == notification_type
    assert result.title == title
    assert result.body == body
    assert result.report_id is None


# TC-2
def test_create_notification_success_with_report(seed_notification_data: None) -> None:
    notification_service = NotificationService()
    user = CORRECT_USER
    notification_type = NotificationType.STATUS_CHANGED
    title = "Status updated"
    body = "The report status has changed."
    report = REPORT_WASTE

    result = notification_service.create_notification(user, notification_type, title, body, report)

    assert isinstance(result, Notification)
    assert result.user_id == user.id
    assert result.notification_type == notification_type
    assert result.title == title
    assert result.body == body
    assert result.report_id == report.id


# TC-3
def test_create_notification_none_user(seed_notification_data: None) -> None:
    notification_service = NotificationService()
    user = None
    notification_type = NotificationType.STATUS_CHANGED
    title = "Status updated"
    body = "The report status has changed."
    report = None

    result = notification_service.create_notification(user, notification_type, title, body, report)

    assert result is None


# TC-4
def test_create_notification_invalid_type(seed_notification_data: None) -> None:
    notification_service = NotificationService()
    user = CORRECT_USER
    notification_type = "123" 
    title = "Status updated"
    body = "The report status has changed."
    report = REPORT_WASTE

    with pytest.raises(ValueError):
        notification_service.create_notification(user, notification_type, title, body, report)