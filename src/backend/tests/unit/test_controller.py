from unittest.mock import Mock
from participium.controllers.operator_controller import OperatorController
from participium.controllers.user_controller import UserController
from participium.models.enums import Role

def test_build_dashboard_with_non_operator_role_returns_empty_pending():
    report_service = Mock()
    notification_service = Mock()
    report_service.list_operator_reports.return_value = []
    notification_service.count_unread_message_notifications_by_report.return_value = {}

    controller = OperatorController(report_service, notification_service)

    user = Mock()
    user.role = Role.CITIZEN  
    user.id = 1

    context = controller.build_dashboard(user)

    assert context.pending_reports == []
    report_service.list_pending_reports.assert_not_called()

def test_list_users_delegates_to_service():
    user_service = Mock()
    user_service.list_users.return_value = []
    controller = UserController(user_service, Mock())

    result = controller.list_users()

    user_service.list_users.assert_called_once()
    assert result == []


def test_create_user_delegates_to_service():
    user_service = Mock()
    user_service.create_user.return_value = Mock()
    controller = UserController(user_service, Mock())

    payload = {"username": "test"}
    controller.create_user(payload)

    user_service.create_user.assert_called_once_with(payload)


def test_update_user_delegates_to_service():
    user_service = Mock()
    user_service.update_user.return_value = Mock()
    controller = UserController(user_service, Mock())

    payload = {"first_name": "Updated"}
    controller.update_user(42, payload)

    user_service.update_user.assert_called_once_with(42, payload)