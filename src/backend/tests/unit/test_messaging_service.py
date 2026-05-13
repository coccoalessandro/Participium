from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.core.exceptions import AuthorizationError, ValidationError
from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report, ReportStatusHistory
from participium.models.user import User
from participium.services.messaging_service import MessagingService



def _user(*, user_id: int, role: Role, category_id: int | None = None) -> Mock:
    return Mock(spec=User, id=user_id, role=role, category_id=category_id)


def _report(*, report_id: int, reporter: Mock, category_id: int = 5) -> Mock:
    return Mock(spec=Report, id=report_id, reporter_id=reporter.id, reporter=reporter, category_id=category_id)



@pytest.fixture
def messaging_bundle() -> dict[str, object]:
    session = Mock()
    message_repository = Mock()
    notification_service = Mock()

    service = MessagingService(
        session=session,
        message_repository=message_repository,
        notification_service=notification_service,
    )
    service._resolve_recipient = Mock()

    return {
        "service": service,
        "session": session,
        "message_repository": message_repository,
        "notification_service": notification_service,
    }


@pytest.fixture
def send_message_success_case(messaging_bundle: dict[str, object]) -> dict[str, object]:
    citizen = _user(user_id=102, role=Role.CITIZEN)
    operator = _user(user_id=104, role=Role.OPERATOR, category_id=5)
    report = _report(report_id=1, reporter=citizen)
    messaging_bundle["service"]._resolve_recipient.return_value = citizen
    messaging_bundle["citizen"] = citizen
    messaging_bundle["operator"] = operator
    messaging_bundle["report"] = report
    return messaging_bundle


@pytest.fixture
def send_message_unauthorized_case(messaging_bundle: dict[str, object]) -> dict[str, object]:
    citizen = _user(user_id=102, role=Role.CITIZEN)
    intruder = _user(user_id=999, role=Role.CITIZEN)
    report = _report(report_id=1, reporter=citizen)
    messaging_bundle["intruder"] = intruder
    messaging_bundle["report"] = report
    return messaging_bundle


@pytest.fixture
def send_message_no_recipient_case(messaging_bundle: dict[str, object]) -> dict[str, object]:
    operator = _user(user_id=104, role=Role.OPERATOR, category_id=5)
    citizen = _user(user_id=102, role=Role.CITIZEN)
    report = _report(report_id=1, reporter=citizen)
    messaging_bundle["service"]._resolve_recipient.return_value = None
    messaging_bundle["operator"] = operator
    messaging_bundle["report"] = report
    return messaging_bundle



def test_send_message_success(send_message_success_case: dict[str, object]) -> None:
    service = send_message_success_case["service"]
    repo = send_message_success_case["message_repository"]
    session = send_message_success_case["session"]
    operator = send_message_success_case["operator"]
    report = send_message_success_case["report"]

    result = service.send_message(report, operator, "Hello, I need more information.")

    assert result is not None
    assert isinstance(result, Message)
    repo.add.assert_called_once()
    session.commit.assert_called_once()


def test_send_message_unauthorized_raises(send_message_unauthorized_case: dict[str, object]) -> None:
    service = send_message_unauthorized_case["service"]
    intruder = send_message_unauthorized_case["intruder"]
    report = send_message_unauthorized_case["report"]

    with pytest.raises(AuthorizationError):
        service.send_message(report, intruder, "Hello")


@pytest.mark.parametrize("invalid_body", ["", "   ", "\n"])
def test_send_message_blank_body_raises(invalid_body: str, send_message_success_case: dict[str, object]) -> None:
    service = send_message_success_case["service"]
    operator = send_message_success_case["operator"]
    report = send_message_success_case["report"]

    with pytest.raises(ValidationError, match="body"):
        service.send_message(report, operator, invalid_body)


def test_send_message_no_recipient_raises(send_message_no_recipient_case: dict[str, object]) -> None:
    service = send_message_no_recipient_case["service"]
    operator = send_message_no_recipient_case["operator"]
    report = send_message_no_recipient_case["report"]

    with pytest.raises(ValidationError, match="recipient"):
        service.send_message(report, operator, "Hello")



@pytest.fixture
def access_thread_report() -> Mock:
    citizen = _user(user_id=102, role=Role.CITIZEN)
    return _report(report_id=1, reporter=citizen, category_id=5)



def test_can_access_thread_none_user_returns_false(messaging_bundle: dict[str, object], access_thread_report: Mock) -> None:
    service = messaging_bundle["service"]

    assert service.can_access_thread(access_thread_report, None) is False


def test_can_access_thread_admin_returns_true(messaging_bundle: dict[str, object], access_thread_report: Mock) -> None:
    service = messaging_bundle["service"]
    admin = _user(user_id=1, role=Role.ADMIN)

    assert service.can_access_thread(access_thread_report, admin) is True


def test_can_access_thread_operator_same_category_returns_true(messaging_bundle: dict[str, object], access_thread_report: Mock) -> None:
    service = messaging_bundle["service"]
    operator = _user(user_id=104, role=Role.OPERATOR, category_id=5)

    assert service.can_access_thread(access_thread_report, operator) is True



def test_list_messages_returns_all_report_messages(messaging_bundle: dict[str, object]) -> None:
    service = messaging_bundle["service"]
    repo = messaging_bundle["message_repository"]
    citizen = _user(user_id=102, role=Role.CITIZEN)
    report = _report(report_id=1, reporter=citizen)
    msg1 = Mock(spec=Message)
    msg2 = Mock(spec=Message)
    repo.list_for_report.return_value = [msg1, msg2]

    result = service.list_messages(report, citizen)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(m, Message) for m in result)
    assert result == [msg1, msg2]



@pytest.fixture
def resolve_bundle() -> dict[str, object]:
    message_repository = Mock()
    service = MessagingService(message_repository=message_repository)

    reporter = User(id=1, role=Role.CITIZEN)
    citizen = User(id=2, role=Role.CITIZEN)
    admin = User(id=3, role=Role.ADMIN)
    operator = User(id=4, role=Role.OPERATOR)

    report = Report(
        id=100,
        reporter=reporter,
        reporter_id=reporter.id,
        status_history=[],
    )

    return {
        "service": service,
        "message_repository": message_repository,
        "report": report,
        "reporter": reporter,
        "citizen": citizen,
        "admin": admin,
        "operator": operator,
    }


def test_resolve_recipient_admin_sender_returns_reporter(resolve_bundle: dict[str, object]) -> None:
    service = resolve_bundle["service"]
    repo = resolve_bundle["message_repository"]
    report = resolve_bundle["report"]
    admin = resolve_bundle["admin"]
    reporter = resolve_bundle["reporter"]

    recipient = service._resolve_recipient(report, admin)

    assert recipient is reporter
    repo.list_for_report.assert_not_called()


def test_resolve_recipient_no_messages_no_status_history_returns_none(resolve_bundle: dict[str, object]) -> None:
    service = resolve_bundle["service"]
    repo = resolve_bundle["message_repository"]
    report = resolve_bundle["report"]
    citizen = resolve_bundle["citizen"]
    repo.list_for_report.return_value = []
    report.status_history = []

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is None
    repo.list_for_report.assert_called_once_with(report.id)


def test_resolve_recipient_admin_message_sender_returned(resolve_bundle: dict[str, object]) -> None:
    service = resolve_bundle["service"]
    repo = resolve_bundle["message_repository"]
    report = resolve_bundle["report"]
    citizen = resolve_bundle["citizen"]
    admin = resolve_bundle["admin"]
    repo.list_for_report.return_value = [Message(id=10, report_id=report.id, sender=admin)]

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is admin
    repo.list_for_report.assert_called_once_with(report.id)


def test_resolve_recipient_operator_from_status_history_returned(resolve_bundle: dict[str, object]) -> None:
    service = resolve_bundle["service"]
    repo = resolve_bundle["message_repository"]
    report = resolve_bundle["report"]
    citizen = resolve_bundle["citizen"]
    operator = resolve_bundle["operator"]
    repo.list_for_report.return_value = []
    report.status_history = [ReportStatusHistory(id=20, report_id=report.id, changed_by=operator)]

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is operator
    repo.list_for_report.assert_called_once_with(report.id)


def test_resolve_recipient_no_valid_messages_or_status_events_returns_none(resolve_bundle: dict[str, object]) -> None:
    service = resolve_bundle["service"]
    repo = resolve_bundle["message_repository"]
    report = resolve_bundle["report"]
    citizen = resolve_bundle["citizen"]
    repo.list_for_report.return_value = [
        Message(id=10, report_id=report.id, sender=None),
        Message(id=11, report_id=report.id, sender=citizen),
    ]
    report.status_history = [
        ReportStatusHistory(id=20, report_id=report.id, changed_by=None),
        ReportStatusHistory(id=21, report_id=report.id, changed_by=citizen),
    ]

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is None
    repo.list_for_report.assert_called_once_with(report.id)