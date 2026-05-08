from __future__ import annotations

from unittest.mock import Mock
import pytest

from participium.services.messaging_service import MessagingService
from participium.models.user import User
from participium.models.report import Report
from participium.models.message import Message
from participium.models.enums import Role
from participium.core.exceptions import ValidationError, AuthorizationError

CORRECT_USER_CITIZEN = Mock(spec=User, id=102, role=Role.CITIZEN)
CORRECT_USER_OPERATOR = Mock(spec=User, id=104, role=Role.OPERATOR, category_id = 5)
UNAUTHORIZED_USER_CITIZEN = Mock(spec=User, id=999, role=Role.CITIZEN)

CORRECT_REPORT = Mock(spec=Report, id=1, reporter_id=102, reporter=CORRECT_USER_CITIZEN, category_id = 5)

@pytest.fixture
def messaging_service_bundle() -> dict[str, object]:
    session = Mock()
    message_repository = Mock()
    notification_service = Mock()
    
    service = MessagingService(
        session=session,
        message_repository=message_repository,
        notification_service=notification_service
    )

    service._resolve_recipient = Mock()
    
    return {
        "service": service,
        "session": session,
        "message_repository": message_repository,
        "notification_service": notification_service
    }

# --- TEST CASES ---

# TC-1
def test_send_message_success(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    repo = messaging_service_bundle["message_repository"]
    
    service._resolve_recipient.return_value = CORRECT_USER_CITIZEN
    
    body = "Hello, I need more information."
    
    result = service.send_message(CORRECT_REPORT, CORRECT_USER_OPERATOR, body)

    assert result is not None
    repo.add.assert_called_once()
    messaging_service_bundle["session"].commit.assert_called_once()
    messaging_service_bundle["notification_service"].create_notification.assert_called_once()

# TC-2
def test_send_message_unauthorized(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    
    with pytest.raises(AuthorizationError):
        service.send_message(CORRECT_REPORT, UNAUTHORIZED_USER_CITIZEN, "Hello")

# TC-3 & TC-4 
@pytest.mark.parametrize("invalid_body", ["", "   ", "\n"])
def test_send_message_invalid_body(invalid_body: str, messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    
    with pytest.raises(ValidationError, match="body"):
        service.send_message(CORRECT_REPORT, CORRECT_USER_CITIZEN, invalid_body)

# TC-5
def test_send_message_no_recipient(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    
    service._resolve_recipient.return_value = None

    with pytest.raises(ValidationError, match="recipient"):
        service.send_message(CORRECT_REPORT, CORRECT_USER_OPERATOR, "Hello")

# TC-6
def test_access_thread_user_none(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    message_repo = messaging_service_bundle["message_repository"]
    
    mock_user = None
    mock_Report = CORRECT_REPORT

    result_permission = service.can_access_thread(mock_Report, mock_user)

    assert result_permission is False

# TC-7
def test_access_thread_user_operator(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    message_repo = messaging_service_bundle["message_repository"]
    
    mock_user = Mock(spec=User)
    mock_user.role = Role.ADMIN
    mock_Report = CORRECT_REPORT

    result_permission = service.can_access_thread(mock_Report, mock_user)

    assert result_permission is True

# TC-8
def test_access_thread_same_category(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    message_repo = messaging_service_bundle["message_repository"]
    
    mock_user = CORRECT_USER_OPERATOR
    mock_Report = CORRECT_REPORT

    result_permission = service.can_access_thread(mock_Report, mock_user)

    assert result_permission is True

# TC-9
def test_list_messages(messaging_service_bundle: dict[str, object]) -> None:
    service = messaging_service_bundle["service"]
    message_repo = messaging_service_bundle["message_repository"]
    
    mock_user = CORRECT_USER_CITIZEN
    mock_Report = CORRECT_REPORT

    mock_msg1 = Mock(spec=Message)
    mock_msg2 = Mock(spec=Message)

    message_repo.list_for_report.return_value = [mock_msg1, mock_msg2]

    result_list = service.list_messages(mock_Report, mock_user)

    assert isinstance(result_list, int)
    assert len(result_list) == 2
    assert all(isinstance(msg, Message) for msg in result_list)
    assert result_list == [mock_msg1, mock_msg2] 

    