from __future__ import annotations

from participium.services.report_service import ReportService
from participium.models.enums import ReportStatus
from datetime import datetime
from participium.models.report import Report

# Function: 
# Inputs: category_id (int | None), status (ReportStatus | None), date_from (datetime | None), date_to (datetime | None), sort (str)
# Expected Output:
# - A list of public `Report` objects matching the filters if the inputs are valid.
#def list_public_reports(
#        self,
#        category_id: int | None = None,
#        status: ReportStatus | None = None,
#        date_from: datetime | None = None,
#        date_to: datetime | None = None,
#        sort: str = "desc",
#    ) -> list[Report]


#TC-1
def test_public_reports_desc(seed_public_reports_data: None) -> None:
    report_service = ReportService()
    category_id = 1
    status = ReportStatus.RESOLVED
    date_from = datetime(2026, 2, 10)
    date_to = datetime(2026, 2, 15)
    sort = "desc"

    report_list = report_service.list_public_reports(category_id, status, date_from, date_to, sort)

    assert isinstance(report_list, list)

    for report in report_list:
        assert isinstance(report, Report)
        assert report.category_id == category_id
        assert report.status == status
        assert report.status_history[0].created_at >= date_from
        assert report.status_history[0].created_at <= date_to

    if len(report_list) > 1:
        dates = [report.status_history[0].created_at for report in report_list]
        assert dates == sorted(dates, reverse=True)

#TC-2
def test_public_reports_asc(seed_public_reports_data: None) -> None:
    report_service = ReportService()
    category_id = 1
    status = ReportStatus.RESOLVED
    date_from = datetime(2026, 2, 10)
    date_to = datetime(2026, 2, 15)
    sort = "asc"

    report_list = report_service.list_public_reports(category_id, status, date_from, date_to, sort)

    assert isinstance(report_list, list)

    for report in report_list:
        assert isinstance(report, Report)
        assert report.category_id == category_id
        assert report.status == status
        assert report.status_history[0].created_at >= date_from
        assert report.status_history[0].created_at <= date_to

    if len(report_list) > 1:
        dates = [report.status_history[0].created_at for report in report_list]
        assert dates == sorted(dates)