from __future__ import annotations

from unittest.mock import Mock, patch
import pytest

from participium.services.notification_service import NotificationService
from participium.models.user import User
from participium.models.report import Report
from participium.models.enums import NotificationType, ReportStatus
from participium.models.notification import Notification
from participium.core.exceptions import AuthorizationError, NotFoundError 

CORRECT_USER = Mock(
    spec=User, 
    id=102, 
    email="luca.bianchi@example.com",
    email_notifications_enabled=True
)

DISABLED_USER = Mock(
    spec=User, 
    id=102, 
    email="luca.bianchi@example.com",
    email_notifications_enabled=False
)

REPORT_WASTE = Mock(
    spec=Report, 
    id=1,
    user_id=102
)


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
        "email_gateway": email_gateway,
    }

# TC-1
def test_create_notification_success(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]

    mock_user = CORRECT_USER
    mock_report = REPORT_WASTE
    
    mock_notification_type = NotificationType.STATUS_CHANGE

    result_notification = service.create_notification(mock_user, mock_notification_type, "notification title", "body" ,mock_report)

    assert isinstance(result_notification, Notification)
    assert result_notification.user_id == mock_user.id
    assert result_notification.type == mock_notification_type
    assert result_notification.title == "notification title"
    assert result_notification.body == "body"
    assert result_notification.report_id == mock_report.id

# TC-2
def test_create_notification_notification_disabled_success(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]

    mock_user = DISABLED_USER
    mock_report = REPORT_WASTE
    
    mock_notification_type = NotificationType.STATUS_CHANGE

    result_notification = service.create_notification(mock_user, mock_notification_type, "notification title", "body" ,mock_report)

    assert isinstance(result_notification, Notification)
    assert result_notification.user_id == mock_user.id
    assert result_notification.type == mock_notification_type
    assert result_notification.title == "notification title"
    assert result_notification.body == "body"
    assert result_notification.report_id == mock_report.id

# TC-3
def test_create_notification_user_is_none(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]

    mock_user = None
    mock_report = REPORT_WASTE
    mock_notification_type = NotificationType.STATUS_CHANGE

    result_notification = service.create_notification(mock_user, mock_notification_type, "notification title", "body" ,mock_report)

    assert result_notification is None
    
# TC-4
def test_create_notification_email_exception_unsuccess(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]

    email_gateway.send.side_effect = Exception("Email notification delivery failed")
    mock_user = CORRECT_USER
    mock_report = REPORT_WASTE
    
    mock_notification_type = NotificationType.STATUS_CHANGE

    result_notification = service.create_notification(mock_user, mock_notification_type, "notification title", "body" ,mock_report)

    assert isinstance(result_notification, Notification)
    assert result_notification.user_id == mock_user.id
    assert result_notification.type == mock_notification_type
    assert result_notification.title == "notification title"
    assert result_notification.body == "body"
    assert result_notification.report_id == mock_report.id

# TC-5
def test_notify_new_message(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]

    mock_user = CORRECT_USER
    mock_report = REPORT_WASTE
    
    service.notify_new_message(mock_user,mock_report, "Sender name", "Body")

# TC-6
def test_list_notifications(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]
    
    mock_user = CORRECT_USER

    mock_ntf1 = Mock(spec=Notification)
    mock_ntf2 = Mock(spec=Notification)

    mock_ntf1.user_id = CORRECT_USER.id
    mock_ntf2.user_id = CORRECT_USER.id

    notification_repo.list_for_user.return_value = [mock_ntf1, mock_ntf2]

    result_list = service.list_notifications(mock_user.id)

    assert isinstance(result_list, list)
    assert len(result_list) == 2
    assert all(isinstance(ntf, Notification) for ntf in result_list)
    assert result_list == [mock_ntf1, mock_ntf2] 

    
# TC-7
def test_mark_notification_as_read_success(notification_service_bundle: dict[str, object]) -> None: 
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]
    
    mock_user = CORRECT_USER
    mock_report = REPORT_WASTE

    mock_ntf1 = Mock(spec=Notification)
    mock_ntf2 = Mock(spec=Notification)

    mock_ntf1.user_id = CORRECT_USER.id
    mock_ntf2.user_id = CORRECT_USER.id
    mock_ntf1.report_id = REPORT_WASTE.id
    mock_ntf2.report_id = REPORT_WASTE.id
    
    mock_ntf1.is_read = False
    mock_ntf2.is_read = False

    notification_repo.list_unread_message_notifications.return_value = [mock_ntf1, mock_ntf2]
    result = service.mark_report_message_notifications_as_read(mock_user.id, mock_report.id)
    assert result == 2 

# TC-8
def test_mark_notification_as_read_empty(notification_service_bundle: dict[str, object]) -> None:
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]
    
    mock_user = CORRECT_USER
    mock_report = REPORT_WASTE

    notification_repo.list_unread_message_notifications.return_value = []
    result = service.mark_report_message_notifications_as_read(mock_user.id, mock_report.id)
    assert result == 0

# TC-9
def test_get_user_notification_none(notification_service_bundle: dict[str, object]) -> None: 
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]
    
    mock_user = CORRECT_USER
    mock_ntf = Mock(spec=Notification)
    mock_ntf.id = 999
    notification_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundError):
        service.get_user_notification(mock_user.id, mock_ntf.id)

# TC-10
def test_get_user_notification_different_id(notification_service_bundle: dict[str, object]) -> None: 
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]
    
    mock_user = CORRECT_USER
    mock_ntf = Mock(spec=Notification)

    mock_ntf.user_id = 100

    with pytest.raises(AuthorizationError):
        service.get_user_notification(mock_user.id, mock_ntf.id)
    
# TC-11
def test_get_user_notification_success(notification_service_bundle: dict[str, object]) -> None: 
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]
    
    mock_user = CORRECT_USER
    mock_ntf = Mock(spec=Notification)
    mock_ntf.user_id = 102
    notification_repo.get_by_id.return_value = mock_ntf

    result_notification = service.get_user_notification(mock_user.id, mock_ntf.id)
    
    assert isinstance(result_notification, Notification)
    assert result_notification.user_id == mock_user.id
    assert result_notification == mock_ntf

# TC-12
def test_mark_as_read_success(notification_service_bundle: dict[str, object]) -> None: 
    service = notification_service_bundle["service"]
    notification_repo = notification_service_bundle["notification_repository"]
    email_gateway = notification_service_bundle["email_gateway"]

    mock_notification = Mock(spec=Notification)
    mock_notification.is_read = False

    result_notification = service.mark_as_read(mock_notification)
    
    assert isinstance(result_notification, Notification)
    assert result_notification.is_read is True
    