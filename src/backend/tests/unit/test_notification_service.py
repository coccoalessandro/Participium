from __future__ import annotations

from unittest.mock import Mock, call

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError
from participium.models.enums import NotificationType
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User
from participium.services.notification_service import NotificationService



def _user(*, user_id: int, email_notifications_enabled: bool = True) -> Mock:
    return Mock(spec=User, id=user_id, email=f"user{user_id}@example.com", email_notifications_enabled=email_notifications_enabled)


def _notification(*, notification_id: int, user_id: int, report_id: int | None = None, is_read: bool = False) -> Notification:
    return Notification(id=notification_id, user_id=user_id, report_id=report_id, is_read=is_read)



@pytest.fixture
def notification_bundle() -> dict[str, object]:
    session = Mock()
    notification_repository = Mock()
    email_gateway = Mock()

    service = NotificationService(
        session=session,
        notification_repository=notification_repository,
        email_gateway=email_gateway,
    )

    return {
        "service": service,
        "session": session,
        "notification_repository": notification_repository,
        "email_gateway": email_gateway,
    }



@pytest.fixture
def user_with_email_enabled_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["user"] = _user(user_id=102)
    notification_bundle["report"] = Mock(spec=Report, id=1)
    return notification_bundle


@pytest.fixture
def user_with_email_disabled_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["user"] = _user(user_id=102, email_notifications_enabled=False)
    notification_bundle["report"] = Mock(spec=Report, id=1)
    return notification_bundle


@pytest.fixture
def email_delivery_failure_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["email_gateway"].send.side_effect = Exception("SMTP failure")
    notification_bundle["user"] = _user(user_id=102)
    notification_bundle["report"] = Mock(spec=Report, id=1)
    return notification_bundle



def test_create_notification_with_email_enabled_success(user_with_email_enabled_case: dict[str, object]) -> None:
    service = user_with_email_enabled_case["service"]
    user = user_with_email_enabled_case["user"]
    report = user_with_email_enabled_case["report"]
    email_gateway = user_with_email_enabled_case["email_gateway"]

    result = service.create_notification(user, NotificationType.STATUS_CHANGE, "title", "body", report)

    assert isinstance(result, Notification)
    assert result.user_id == user.id
    assert result.report_id == report.id
    assert result.type == NotificationType.STATUS_CHANGE
    assert result.title == "title"
    assert result.body == "body"
    email_gateway.send.assert_called_once()


def test_create_notification_with_email_disabled_skips_send(user_with_email_disabled_case: dict[str, object]) -> None:
    service = user_with_email_disabled_case["service"]
    user = user_with_email_disabled_case["user"]
    report = user_with_email_disabled_case["report"]
    email_gateway = user_with_email_disabled_case["email_gateway"]

    result = service.create_notification(user, NotificationType.STATUS_CHANGE, "title", "body", report)

    assert isinstance(result, Notification)
    assert result.user_id == user.id
    email_gateway.send.assert_not_called()


def test_create_notification_with_null_user_returns_none(notification_bundle: dict[str, object]) -> None:
    service = notification_bundle["service"]
    report = Mock(spec=Report, id=1)

    result = service.create_notification(None, NotificationType.STATUS_CHANGE, "title", "body", report)

    assert result is None


def test_create_notification_email_failure_is_swallowed(email_delivery_failure_case: dict[str, object]) -> None:
    service = email_delivery_failure_case["service"]
    user = email_delivery_failure_case["user"]
    report = email_delivery_failure_case["report"]

    result = service.create_notification(user, NotificationType.STATUS_CHANGE, "title", "body", report)

    assert isinstance(result, Notification)
    assert result.user_id == user.id



def test_notify_new_message_delegates_to_create_notification(notification_bundle: dict[str, object]) -> None:
    service = notification_bundle["service"]
    service.create_notification = Mock()
    user = _user(user_id=102)
    report = Mock(spec=Report, id=1)

    service.notify_new_message(user, report, "Mario Rossi", "body text")

    service.create_notification.assert_called_once_with(
        user,
        NotificationType.MESSAGE,
        f"New message on report #{report.id}",
        "Mario Rossi: body text",
        report=report,
    )


@pytest.fixture
def notify_status_bundle(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["service"].create_notification = Mock()
    return notification_bundle


def test_notify_status_change_empty_recipients_does_not_notify(notify_status_bundle: dict[str, object]) -> None:
    service = notify_status_bundle["service"]
    report = Mock(id=1)

    service.notify_status_change(recipients=[], report=report, body="update")

    service.create_notification.assert_not_called()


def test_notify_status_change_filters_none_and_duplicates(notify_status_bundle: dict[str, object]) -> None:
    service = notify_status_bundle["service"]
    report = Mock(id=1)
    user = Mock(id=102)

    service.notify_status_change(recipients=[user, None, user], report=report, body="update")

    assert service.create_notification.call_count == 1


def test_notify_status_change_notifies_each_unique_recipient(notify_status_bundle: dict[str, object]) -> None:
    service = notify_status_bundle["service"]
    report = Mock(id=1)
    user1 = Mock(id=102)
    user2 = Mock(id=103)
    body = "Status updated"

    service.notify_status_change(recipients=[user1, user2], report=report, body=body)

    service.create_notification.assert_has_calls(
        [
            call(user1, NotificationType.STATUS_CHANGE, f"Report #{report.id} status updated", body, report=report),
            call(user2, NotificationType.STATUS_CHANGE, f"Report #{report.id} status updated", body, report=report),
        ],
        any_order=True,
    )
    assert service.create_notification.call_count == 2


def test_list_notifications_returns_all_user_notifications(notification_bundle: dict[str, object]) -> None:
    service = notification_bundle["service"]
    repo = notification_bundle["notification_repository"]
    ntf1 = Mock(spec=Notification, user_id=102)
    ntf2 = Mock(spec=Notification, user_id=102)
    repo.list_for_user.return_value = [ntf1, ntf2]

    result = service.list_notifications(user_id=102)

    assert result == [ntf1, ntf2]
    repo.list_for_user.assert_called_once_with(102)



@pytest.fixture
def empty_unread_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["notification_repository"].list_unread_message_notifications.return_value = []
    return notification_bundle


@pytest.fixture
def mixed_unread_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    n1 = Mock(report_id=None)
    n2 = Mock(report_id=10)
    n3 = Mock(report_id=10)
    notification_bundle["notification_repository"].list_unread_message_notifications.return_value = [n1, n2, n3]
    return notification_bundle


def test_count_unread_notifications_with_no_results_returns_empty_dict(empty_unread_case: dict[str, object]) -> None:
    service = empty_unread_case["service"]
    repo = empty_unread_case["notification_repository"]

    result = service.count_unread_message_notifications_by_report(user_id=1)

    assert result == {}
    repo.list_unread_message_notifications.assert_called_once_with(user_id=1)


def test_count_unread_notifications_skips_null_report_id(mixed_unread_case: dict[str, object]) -> None:
    service = mixed_unread_case["service"]
    repo = mixed_unread_case["notification_repository"]

    result = service.count_unread_message_notifications_by_report(user_id=1)

    assert result == {10: 2}
    repo.list_unread_message_notifications.assert_called_once_with(user_id=1)


@pytest.fixture
def unread_notifications_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notifications = [
        _notification(notification_id=201, user_id=102, report_id=1),
        _notification(notification_id=202, user_id=102, report_id=1),
    ]
    notification_bundle["notification_repository"].list_unread_message_notifications.return_value = notifications
    notification_bundle["notifications"] = notifications
    return notification_bundle


@pytest.fixture
def no_unread_notifications_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["notification_repository"].list_unread_message_notifications.return_value = []
    return notification_bundle


def test_mark_report_notifications_as_read_marks_all_and_commits(unread_notifications_case: dict[str, object]) -> None:
    service = unread_notifications_case["service"]
    session = unread_notifications_case["session"]
    notifications = unread_notifications_case["notifications"]

    result = service.mark_report_message_notifications_as_read(user_id=102, report_id=1)

    assert result == 2
    assert all(n.is_read is True for n in notifications)
    session.commit.assert_called_once()


def test_mark_report_notifications_as_read_returns_zero_without_commit(no_unread_notifications_case: dict[str, object]) -> None:
    service = no_unread_notifications_case["service"]
    session = no_unread_notifications_case["session"]

    result = service.mark_report_message_notifications_as_read(user_id=102, report_id=1)

    assert result == 0
    session.commit.assert_not_called()



@pytest.fixture
def notification_found_same_user_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    ntf = Mock(spec=Notification, id=1, user_id=102)
    notification_bundle["notification_repository"].get_by_id.return_value = ntf
    notification_bundle["notification"] = ntf
    return notification_bundle


@pytest.fixture
def notification_not_found_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    notification_bundle["notification_repository"].get_by_id.return_value = None
    return notification_bundle


@pytest.fixture
def notification_different_user_case(notification_bundle: dict[str, object]) -> dict[str, object]:
    ntf = Mock(spec=Notification, id=1, user_id=999)
    notification_bundle["notification_repository"].get_by_id.return_value = ntf
    notification_bundle["notification"] = ntf
    return notification_bundle



def test_get_user_notification_success(notification_found_same_user_case: dict[str, object]) -> None:
    service = notification_found_same_user_case["service"]
    ntf = notification_found_same_user_case["notification"]

    result = service.get_user_notification(user_id=102, notification_id=ntf.id)

    assert isinstance(result, Notification)
    assert result.user_id == 102
    assert result == ntf


def test_get_user_notification_not_found_raises(notification_not_found_case: dict[str, object]) -> None:
    service = notification_not_found_case["service"]

    with pytest.raises(NotFoundError):
        service.get_user_notification(user_id=102, notification_id=999)


def test_get_user_notification_wrong_owner_raises(notification_different_user_case: dict[str, object]) -> None:
    service = notification_different_user_case["service"]
    ntf = notification_different_user_case["notification"]

    with pytest.raises(AuthorizationError):
        service.get_user_notification(user_id=102, notification_id=ntf.id)



def test_mark_as_read_sets_flag_and_commits(notification_bundle: dict[str, object]) -> None:
    service = notification_bundle["service"]
    session = notification_bundle["session"]
    ntf = Mock(spec=Notification, is_read=False)

    result = service.mark_as_read(ntf)

    assert isinstance(result, Notification)
    assert result.is_read is True
    session.commit.assert_called_once()