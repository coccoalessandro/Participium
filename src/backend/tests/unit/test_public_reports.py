from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock
import pytest

from participium.services.report_service import ReportService
from participium.models.enums import ReportStatus
from participium.models.report import Report

# --- FIXTURE DEL SERVIZIO ---

@pytest.fixture
def report_service_list_bundle() -> dict[str, object]:
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
    
    return {
        "service": service,
        "report_repository": report_repository,
    }


# --- TEST CASES (Unit Tests isolati) ---

# TC-1
def test_public_reports_desc(report_service_list_bundle: dict[str, object]) -> None:
    service = report_service_list_bundle["service"]
    repo = report_service_list_bundle["report_repository"]
    
    # Prepariamo i dati
    category_id = 1
    status = ReportStatus.RESOLVED
    date_from = datetime(2026, 2, 10)
    date_to = datetime(2026, 2, 15)
    sort = "desc"
    
    # 1. Copione: Diciamo al finto DB di restituire una finta lista di report
    fake_reports = [Mock(spec=Report), Mock(spec=Report)]
    
    # (NOTA: Se il metodo nel tuo file si chiama diversamente da 'list_public', cambialo qui sotto!)
    repo.list_public.return_value = fake_reports

    # 2. Azione: Eseguiamo il servizio
    report_list = service.list_public_reports(category_id, status, date_from, date_to, sort)

    # 3. Verifica: Controlliamo che il servizio restituisca esattamente ciò che ha detto il DB
    assert report_list == fake_reports
    
    # 4. Verifica da Cecchino: Il servizio ha passato i parametri giusti al DB?
    repo.list_public.assert_called_once_with(
        category_id=category_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort=sort
    )


# TC-2
def test_public_reports_asc(report_service_list_bundle: dict[str, object]) -> None:
    service = report_service_list_bundle["service"]
    repo = report_service_list_bundle["report_repository"]
    
    category_id = 1
    status = ReportStatus.RESOLVED
    date_from = datetime(2026, 2, 10)
    date_to = datetime(2026, 2, 15)
    sort = "asc"
    
    fake_reports = [Mock(spec=Report), Mock(spec=Report)]
    repo.list_public.return_value = fake_reports

    report_list = service.list_public_reports(category_id, status, date_from, date_to, sort)

    assert report_list == fake_reports
    
    # Assicuriamoci che abbia "chiesto" al DB l'ordinamento 'asc'
    repo.list_public.assert_called_once_with(
        category_id=category_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort=sort
    )