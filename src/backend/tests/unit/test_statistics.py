from __future__ import annotations

from unittest.mock import Mock
import pytest
from datetime import datetime

from participium.services.statistics_service import StatisticsService
from participium.models.enums import ReportStatus

@pytest.fixture
def statistics_service_bundle() -> dict[str, object]:
    mock_repo = Mock()
    
    service = StatisticsService(report_repository=mock_repo)
    
    return {
        "service": service,
        "report_repository": mock_repo
    }

# TC-1
def test_public_statistics_success(statistics_service_bundle: dict[str, object]) -> None:
    service = statistics_service_bundle["service"]
    repo = statistics_service_bundle["report_repository"]
    
    r1 = Mock()
    r1.category.name = "Waste"
    r1.created_at = datetime(2026, 1, 15)
    
    r2 = Mock()
    r2.category.name = "Waste" 
    r2.created_at = datetime(2026, 1, 16)
    
    repo.list_reports.return_value = [r1, r2]
    
    result = service.public_statistics(granularity="day")
    
    repo.list_reports.assert_called_once_with(public_only=True)
    
    assert result["total_reports"] == 2
    assert result["reports_by_category"] == {"Waste": 2}
    assert result["trends"] == {"2026-01-15": 1, "2026-01-16": 1}


# TC-2
def test_admin_statistics_success(statistics_service_bundle: dict[str, object]) -> None:
    service = statistics_service_bundle["service"]
    repo = statistics_service_bundle["report_repository"]
    
    r1 = Mock()
    r1.category.name = "Waste"
    r1.status = ReportStatus.RESOLVED
    r1.reporter.username = "mario"
    r1.reporter.id = 1
    
    r2 = Mock()
    r2.category.name = "Public Lighting"
    r2.status = ReportStatus.PENDING_APPROVAL
    r2.reporter = None 
    
    repo.list_all.return_value = [r1, r2]
    
    res = service.admin_statistics()
    
    repo.list_all.assert_called_once()
    
    assert res["reports_by_status"] == {
        ReportStatus.RESOLVED.value: 1, 
        ReportStatus.PENDING_APPROVAL.value: 1
    }
    
    assert res["reports_by_type"] == {"Waste": 1, "Public Lighting": 1}

    assert res["reports_by_type_and_status"] == {
        f"Waste | {ReportStatus.RESOLVED.value}": 1, 
        f"Public Lighting | {ReportStatus.PENDING_APPROVAL.value}": 1
    }
    
    assert res["reports_by_reporter"] == {
        "mario (1)": 1, 
        "Deleted Citizen": 1
    }
    
    assert res["reports_by_reporter_and_type"] == {
        "mario (1) | Waste": 1, 
        "Deleted Citizen | Public Lighting": 1
    }
    
    assert res["reports_by_reporter_type_and_status"] == {
        f"mario (1) | Waste | {ReportStatus.RESOLVED.value}": 1, 
        f"Deleted Citizen | Public Lighting | {ReportStatus.PENDING_APPROVAL.value}": 1
    }
    
    assert isinstance(res["top_1_percent_by_type"], dict)
    assert isinstance(res["top_5_percent_by_type"], dict)

# TC-3
def test_aggregate_trends(statistics_service_bundle: dict[str, object]) -> None:
    service = statistics_service_bundle["service"]
    
    r1 = Mock()
    r1.created_at = datetime(2026, 1, 15)
    r2 = Mock()
    r2.created_at = datetime(2026, 1, 16) 
    
    reports = [r1, r2]
    
    res_day = service._aggregate_trends(reports, "day")
    assert res_day == {"2026-01-15": 1, "2026-01-16": 1}
    
    res_month = service._aggregate_trends(reports, "month")
    assert res_month == {"2026-01": 2}
    
    res_week = service._aggregate_trends(reports, "week")
    assert res_week == {"2026-W03": 2}


# TC-4
def test_reporter_label_with_user() -> None:
    mock_report = Mock()
    mock_report.reporter.username = "mario.rossi"
    mock_report.reporter.id = 10
    
    result = StatisticsService._reporter_label(mock_report)
    assert result == "mario.rossi (10)"

# TC-5
def test_reporter_label_deleted_user() -> None:
    mock_report = Mock()
    mock_report.reporter = None
    
    result = StatisticsService._reporter_label(mock_report)
    assert result == "Deleted Citizen"