from __future__ import annotations

from unittest.mock import Mock

import pytest

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
    return {
        "service": service,
        "session": session,
        "notification_repository": notification_repository,
    }


def test_notification_counts_path_a_empty(
    notification_service_bundle: dict[str, object],
) -> None:
    service = notification_service_bundle["service"]
    repo = notification_service_bundle["notification_repository"]
    
    repo.list_unread_message_notifications.return_value = []
    
    result = service.count_unread_message_notifications_by_report(user_id=1)
    
    assert result == {}
    repo.list_unread_message_notifications.assert_called_once_with(user_id=1)


def test_notification_counts_path_b_and_c_mixed(
    notification_service_bundle: dict[str, object],
) -> None:
    service = notification_service_bundle["service"]
    repo = notification_service_bundle["notification_repository"]
    
    n1 = Mock(report_id=None)
    n2 = Mock(report_id=10)
    n3 = Mock(report_id=10)
    
    repo.list_unread_message_notifications.return_value = [n1, n2, n3]
    
    result = service.count_unread_message_notifications_by_report(user_id=1)
    
    assert result == {10: 2}
    repo.list_unread_message_notifications.assert_called_once_with(user_id=1)