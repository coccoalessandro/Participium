from __future__ import annotations

from participium.services.messaging_service import MessagingService
from participium.models.user import User
from participium.models.report import Report
from participium.models.message import Message
from participium.models.report import ReportStatus 
from participium.models.category import Category
from participium.models.enums import Role

import pytest

from participium.core.exceptions import ValidationError, AuthorizationError

# Function: 
# Inputs: report(Report), sender(User), body(str)
# Expected Output:
# - The persisted `Message` if the message is sent successfully.
# - AuthorizationError if the sender cannot access the thread.
# - ValidationError if the body is empty or blank after trimming.
# - ValidationError if no recipient can currently be resolved for the conversation.
#def send_message(self, report: Report, sender: User, body: str) -> Message

CORRECT_USER_CITIZEN = User(
    id=102,
    username="luca.bianchi",
    first_name="Luca",
    last_name="Bianchi",
    email="luca.bianchi@example.com",
    password_hash="HASHED_PASSWORD_102",
    is_active=True,
    is_email_verified=True,
    role=Role.CITIZEN
)

CORRECT_USER_OPERATOR = User(
    id=104,
    username="filippo.neri",
    first_name="Filippo",
    last_name="Neri",
    email="filippo.neri@example.com",
    password_hash="HASHED_PASSWORD_104",
    is_active=True,
    is_email_verified=True,
    role=Role.OPERATOR
)

UNAUTHORIZED_USER_CITIZEN = User(
    id=999, username="mario.rossi", first_name="Mario", last_name="Rossi",
    email="mario.rossi@example.com", password_hash="HASHED", is_active=True,
    is_email_verified=True, role=Role.CITIZEN
)

CORRECT_CATEGORY = Category(
    1, "Waste", True
)

CORRECT_REPORT = Report(
    id = None,
    title = "Titolo Valido",
    description = "Descrizione valida",
    latitude = 45.0,
    longitude = 9.0,
    is_anonymous = False,
    status = ReportStatus.PENDING_APPROVAL,
    rejection_reason = None,
    reporter_id = 102,
    category_id = 1,
    reporter = CORRECT_USER_CITIZEN,
    category = CORRECT_CATEGORY,
    photos = ["foto1.jpg"],
    status_history = [],
    followers = [],
    messages = []
)

ANONYMOUS_REPORT = Report(
    id = None,
    title = "Titolo Valido",
    description = "Descrizione valida",
    latitude = 45.0,
    longitude = 9.0,
    is_anonymous = True,
    status = ReportStatus.PENDING_APPROVAL,
    rejection_reason = None,
    reporter_id = None,
    category_id = 1,
    reporter = CORRECT_USER_CITIZEN,
    category = CORRECT_CATEGORY,
    photos = ["foto1.jpg"],
    status_history = [],
    followers = [],
    messages = []
)


# TC-1
def test_send_message_success(seed_message_data: None) -> None:
    message_service = MessagingService()
    report = CORRECT_REPORT
    sender = CORRECT_USER_CITIZEN
    body = "Hello, I need more information."

    result_message = message_service.send_message(report, sender, body)

    assert isinstance(result_message, Message)
    assert result_message.report_id == report.id
    assert result_message.sender_id == sender.id
    assert result_message.body == body


# TC-2
def test_send_message_unauthorized(seed_message_data: None) -> None:
    message_service = MessagingService()
    report = CORRECT_REPORT
    sender = UNAUTHORIZED_USER_CITIZEN  
    body = "Hello, I need more information."

    with pytest.raises(AuthorizationError):
        message_service.send_message(report, sender, body)


# TC-3
def test_send_message_empty_body(seed_message_data: None) -> None:
    message_service = MessagingService()
    report = CORRECT_REPORT
    sender = CORRECT_USER_CITIZEN
    body = ""

    with pytest.raises(ValidationError):
        message_service.send_message(report, sender, body)


# TC-4
def test_send_message_blank_body(seed_message_data: None) -> None:
    message_service = MessagingService()
    report = CORRECT_REPORT
    sender = CORRECT_USER_CITIZEN
    body = "    "  

    with pytest.raises(ValidationError):
        message_service.send_message(report, sender, body)


# TC-5
def test_send_message_no_recipient(seed_message_data: None) -> None:
    message_service = MessagingService()
    report = ANONYMOUS_REPORT  
    sender = CORRECT_USER_OPERATOR
    body = "Hello, I need more information."

    with pytest.raises(ValidationError):
        message_service.send_message(report, sender, body)