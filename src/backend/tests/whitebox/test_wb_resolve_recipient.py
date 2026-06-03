from __future__ import annotations
import pytest
from unittest.mock import Mock

from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report, ReportStatusHistory
from participium.models.user import User
from participium.services.messaging_service import MessagingService

pytestmark = pytest.mark.whitebox

@pytest.fixture
def service_bundle():
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


# TC1: sender is ADMIN -> returns report.reporter
def test_resolve_recipient_sender_is_admin(service_bundle):
    service = service_bundle["service"]
    message_repository = service_bundle["message_repository"]
    report = service_bundle["report"]
    reporter = service_bundle["reporter"]
    admin = service_bundle["admin"]

    recipient = service._resolve_recipient(report, admin)

    assert recipient is reporter
    message_repository.list_for_report.assert_not_called()

# TC2: no messages, empty status history -> returns None
def test_resolve_recipient_no_messages_and_no_status_events(service_bundle):
    service = service_bundle["service"]
    message_repository = service_bundle["message_repository"]
    report = service_bundle["report"]
    citizen = service_bundle["citizen"]

    message_repository.list_for_report.return_value = []
    report.status_history = []

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is None
    message_repository.list_for_report.assert_called_once_with(report.id)

# TC3: messages with valid previous ADMIN sender -> returns the ADMIN message.sender 
def test_resolve_recipient_returns_admin_message_sender(service_bundle):
    service = service_bundle["service"]
    message_repository = service_bundle["message_repository"]
    report = service_bundle["report"]
    citizen = service_bundle["citizen"]
    admin = service_bundle["admin"]

    message_repository.list_for_report.return_value = [
        Message(
            id=10,
            report_id=report.id,
            sender=admin,
        )
    ]

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is admin
    message_repository.list_for_report.assert_called_once_with(report.id)

# TC4: no valid messages, one status-history event with OPERATOR changed_by -> returns the OPERATOR user from the status history
def test_resolve_recipient_returns_operator_from_status_history(service_bundle):
    service = service_bundle["service"]
    message_repository = service_bundle["message_repository"]
    report = service_bundle["report"]
    citizen = service_bundle["citizen"]
    operator = service_bundle["operator"]

    message_repository.list_for_report.return_value = []

    report.status_history = [
        ReportStatusHistory(
            id=20,
            report_id=report.id,
            changed_by=operator,
        )
    ]

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is operator
    message_repository.list_for_report.assert_called_once_with(report.id)

# TC5: no valid messages, no valid status-history events -> returns None
def test_resolve_recipient_returns_none_with_invalid_messages_and_status_events(service_bundle):
    service = service_bundle["service"]
    message_repository = service_bundle["message_repository"]
    report = service_bundle["report"]
    citizen = service_bundle["citizen"]

    message_repository.list_for_report.return_value = [
        Message(
            id=10,
            report_id=report.id,
            sender=None,
        ),
        Message(
            id=11,
            report_id=report.id,
            sender=citizen,
        ),
    ]

    report.status_history = [
        ReportStatusHistory(
            id=20,
            report_id=report.id,
            changed_by=None,
        ),
        ReportStatusHistory(
            id=21,
            report_id=report.id,
            changed_by=citizen,
        ),
    ]

    recipient = service._resolve_recipient(report, citizen)

    assert recipient is None
    message_repository.list_for_report.assert_called_once_with(report.id)