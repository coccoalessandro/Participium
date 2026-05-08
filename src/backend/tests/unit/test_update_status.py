from __future__ import annotations

from unittest.mock import Mock
import pytest

from participium.services.report_service import ReportService
from participium.models.user import User
from participium.models.report import Report
from participium.models.enums import Role, ReportStatus
from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError

# --- COSTANTI (Trasformate in Mock per evitare errori SQLAlchemy) ---

OPERATOR_USER = Mock(spec=User, id=102, role=Role.OPERATOR, category_id=1)
CITIZEN_USER = Mock(spec=User, id=102, role=Role.CITIZEN, category_id=None)

REPORT_WASTE = Mock(
    spec=Report, 
    id=1, 
    title="Waste Report", 
    status=ReportStatus.PENDING_APPROVAL, 
    rejection_reason=None, 
    category_id=1
)

REPORT_PUBLIC_LIGHTING = Mock(
    spec=Report, 
    id=2, 
    title="Public Lighting Report", 
    status=ReportStatus.PENDING_APPROVAL, 
    rejection_reason=None, 
    category_id=2
)


# --- FIXTURE DEL SERVIZIO ---

@pytest.fixture
def report_service_update_bundle() -> dict[str, object]:
    session = Mock()
    category_repository = Mock()
    report_repository = Mock()
    storage_service = Mock()
    
    service = ReportService(
        session=session,
        category_repository=category_repository,
        report_repository=report_repository,
        storage_service=storage_service,
    )
    
    # Molti servizi usano un metodo interno o il repo per recuperare il report
    service.get_report = Mock()
    
    return {
        "service": service,
        "session": session,
        "report_repository": report_repository,
    }

# --- TEST CASES ---

# TC-1
def test_update_status_success_1(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    # Configuriamo il Mock per far finta di aver trovato il report
    service.get_report.return_value = REPORT_WASTE
    
    updated_report = service.update_status(
        report_id=1, 
        operator=OPERATOR_USER, 
        next_status_value="Assigned", 
        note=None
    )

    assert updated_report.status == ReportStatus.ASSIGNED
    report_service_update_bundle["session"].commit.assert_called_once()


# TC-2
def test_update_status_unsucess_unauthorized(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    
    with pytest.raises(AuthorizationError):
        service.update_status(
            report_id=1, 
            operator=CITIZEN_USER, 
            next_status_value="Assigned", 
            note=None
        )


# TC-3
def test_update_status_unsucess_different_category(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    # Il report è "Public Lighting" (categoria 2), l'operatore è "Waste" (categoria 1)
    service.get_report.return_value = REPORT_PUBLIC_LIGHTING

    with pytest.raises(AuthorizationError):
        service.update_status(
            report_id=2, 
            operator=OPERATOR_USER, 
            next_status_value="Assigned", 
            note=None
        )


# TC-4
def test_update_status_unsucess_non_existing_report(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    # Il report non esiste
    service.get_report.side_effect = NotFoundError("Report non trovato")

    with pytest.raises(NotFoundError):
        service.update_status(
            report_id=3, 
            operator=OPERATOR_USER, 
            next_status_value="Assigned", 
            note=None
        )


# TC-5
def test_update_status_unsucess_invalid_status(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    service.get_report.return_value = REPORT_WASTE

    with pytest.raises(ValidationError):
        service.update_status(
            report_id=1, 
            operator=OPERATOR_USER, 
            next_status_value="status_inventato", 
            note=None
        )


# TC-6
def test_update_status_unsucess_rejected(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    service.get_report.return_value = REPORT_WASTE

    with pytest.raises(ValidationError, match="note"): # Supponendo che l'errore citi la nota mancante
        service.update_status(
            report_id=1, 
            operator=OPERATOR_USER, 
            next_status_value="Rejected", 
            note=""
        )


# TC-7
def test_update_status_success_rejected(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    service.get_report.return_value = REPORT_WASTE

    updated_report = service.update_status(
        report_id=1, 
        operator=OPERATOR_USER, 
        next_status_value="Rejected", 
        note="Not enough information"
    )

    assert updated_report.status == ReportStatus.REJECTED
    assert updated_report.rejection_reason == "Not enough information"
    report_service_update_bundle["session"].commit.assert_called_once()


# TC-8
def test_update_status_unsucess_valid_not_allowed_status(report_service_update_bundle: dict[str, object]) -> None:
    service = report_service_update_bundle["service"]
    # Il report è in PENDING_APPROVAL. Passare a RESOLVED direttamente viola il flusso di lavoro.
    REPORT_WASTE.status = ReportStatus.PENDING_APPROVAL
    service.get_report.return_value = REPORT_WASTE

    with pytest.raises(ValidationError):
        service.update_status(
            report_id=1, 
            operator=OPERATOR_USER, 
            next_status_value="Resolved", 
            note=None
        )