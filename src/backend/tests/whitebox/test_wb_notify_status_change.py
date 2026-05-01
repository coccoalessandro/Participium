from __future__ import annotations

from unittest.mock import Mock, call

import pytest

from participium.models.enums import NotificationType
from participium.services.notification_service import NotificationService

pytestmark = pytest.mark.whitebox


@pytest.fixture
def notification_service_bundle() -> dict[str, object]:
    session = Mock()
    notification_repository = Mock()
    email_gateway = Mock()
    service = NotificationService(
        session=session,
        notification_repository=notification_repository,
        email_gateway=email_gateway,
    )
    service.create_notification = Mock()
    
    return {
        "service": service,
        "session": session,
        "notification_repository": notification_repository,
    }


def test_notify_status_change_path_a_empty_list(
    notification_service_bundle: dict[str, object],
) -> None:
    #Path A: Loop condition False (0 iterations).
    service = notification_service_bundle["service"]
    report = Mock(id=123)

    service.notify_status_change(recipients=[], report=report, body="Test body")

    service.create_notification.assert_not_called()


def test_notify_status_change_path_b_filtering_none_and_duplicates(
    notification_service_bundle: dict[str, object],
) -> None:
    """Path B: Loop True -> If True (None and duplicate IDs)."""
    service = notification_service_bundle["service"]
    report = Mock(id=123)
    user1 = Mock(id=102)
    
    # recipients[0] -> valid, recipients[1] -> None (C1), recipients[2] -> duplicate (C2)
    recipients = [user1, None, user1]

    service.notify_status_change(recipients=recipients, report=report, body="Status updated")

    assert service.create_notification.call_count == 1


def test_notify_status_change_path_c_success_multiple_recipients(
    notification_service_bundle: dict[str, object],
) -> None:
    #Path C: Loop True -> If False (Successful notification).
    service = notification_service_bundle["service"]
    report = Mock(id=123)
    user1 = Mock(id=102)
    user2 = Mock(id=103)
    body_text = "New Status Update"

    service.notify_status_change(recipients=[user1, user2], report=report, body=body_text)

    expected_calls = [
        call(user1, NotificationType.STATUS_CHANGE, f"Report #{report.id} status updated", body_text, report=report),
        call(user2, NotificationType.STATUS_CHANGE, f"Report #{report.id} status updated", body_text, report=report)
    ]
    service.create_notification.assert_has_calls(expected_calls, any_order=True)
    assert service.create_notification.call_count == 2