from __future__ import annotations

import pytest

from participium.services.report_service import ReportService

from participium.models.user import User
from participium.models.report import Report
from participium.models.enums import Role
from participium.models.enums import ReportStatus
from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError

# Function: 
# Inputs: report_id(int), operator(User), next_status_value(str), note(str | None)
# Expected Output:
# - The updated `Report`, reloaded after persistence if the transition is successful.
# - AuthorizationError if the operator is not allowed to update report statuses or tries to update a report outside their category.
# - NotFoundError if the report does not exist.
# - ValidationError if `next_status_value` is not a valid report status, if a rejection is requested without a note, or if the transition is not allowed by the workflow rules.
#def update_status(
#        self,
#        report_id: int,
#        operator: User,
#        next_status_value: str,
#        note: str | None = None,
#    ) -> Report


OPERATOR_USER = User(
    id=102,
    username="luca.bianchi",
    first_name="Luca",
    last_name="Bianchi",
    email="luca.bianchi@example.com",
    password_hash="HASHED_PASSWORD_102",
    is_active=True,
    is_email_verified=True,
    role = Role.OPERATOR,
    category = "Waste"
)

CITIZEN_USER = User(
    id=102,
    username="luca.bianchi",
    first_name="Luca",
    last_name="Bianchi",
    email="luca.bianchi@example.com",
    password_hash="HASHED_PASSWORD_102",
    is_active=True,
    is_email_verified=True,
    role = Role.CITIZEN,
    category = None
)

REPORT_WASTE = Report(
    id = 1,
    title = "Waste Report",
    status = ReportStatus.PENDING_APPROVAL,
    rejection_reason = None,
    category_id = 1,
    category = "Waste"
)

REPORT_PUBLIC_LIGHTING = Report(
    id = 2,
    title = "Public Lighting Report",
    status = ReportStatus.PENDING_APPROVAL,
    rejection_reason = None,
    category_id = 2,
    category = "Public Lighting"
)

#TC-1
def test_update_status_success_1(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 1
    operator = OPERATOR_USER
    next_status_value = "Assigned"
    note = None

    updated_report = report_service.update_status(report_id, operator, next_status_value, note)

    assert isinstance(updated_report, Report)
    assert updated_report.id == REPORT_WASTE.id
    assert updated_report.title == REPORT_WASTE.title
    assert updated_report.status == ReportStatus.ASSIGNED
    assert updated_report.rejection_reason == REPORT_WASTE.rejection_reason
    assert updated_report.category_id == REPORT_WASTE.category_id
    assert updated_report.category == REPORT_WASTE.category

#TC-2
def test_update_status_unsucess_unauthorized(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 1
    operator = CITIZEN_USER
    next_status_value = "Assigned"
    note = None

    with pytest.raises(AuthorizationError):
        report_service.update_status(report_id, operator, next_status_value, note)


#TC-3
def test_update_status_unsucess_different_category(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 2
    operator = OPERATOR_USER
    next_status_value = "Assigned"
    note = None

    with pytest.raises(AuthorizationError):
        report_service.update_status(report_id, operator, next_status_value, note)

#TC-4
def test_update_status_unsucess_non_existing_report(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 3
    operator = OPERATOR_USER
    next_status_value = "Assigned"
    note = None

    with pytest.raises(NotFoundError):
        report_service.update_status(report_id, operator, next_status_value, note)

#TC-5
def test_update_status_unsucess_invalid_status(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 1
    operator = OPERATOR_USER
    next_status_value = "status"
    note = None

    with pytest.raises(ValidationError):
        report_service.update_status(report_id, operator, next_status_value, note)

#TC-6
def test_update_status_unsucess_rejected(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 1
    operator = OPERATOR_USER
    next_status_value = "Rejected"
    note = ""

    with pytest.raises(ValidationError):
        report_service.update_status(report_id, operator, next_status_value, note)

#TC-7
def test_update_status_success_rejected(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 1
    operator = OPERATOR_USER
    next_status_value = "Rejected"
    note = "Not enough information"

    updated_report = report_service.update_status(report_id, operator, next_status_value, note)

    assert isinstance(updated_report, Report)
    assert updated_report.id == REPORT_WASTE.id
    assert updated_report.title == REPORT_WASTE.title
    assert updated_report.status == ReportStatus.REJECTED
    assert updated_report.rejection_reason == note
    assert updated_report.category_id == REPORT_WASTE.category_id
    assert updated_report.category == REPORT_WASTE.category


#TC-8
def test_update_status_unsucess_valid_not_allowed_status(seed_update_status_data: None) -> None:
    report_service = ReportService()
    report_id = 1
    operator = OPERATOR_USER
    next_status_value = "Resolved"
    note = None

    with pytest.raises(ValidationError):
        report_service.update_status(report_id, operator, next_status_value, note)