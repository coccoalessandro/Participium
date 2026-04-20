from __future__ import annotations

from participium.services.report_service import ReportService

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
#| TC-ID | category_id | status | date_from | date_to | sort | Input |Expected | Fixture |
#| :---- | :---------- | :----- | :-------- | :------ | :--- | :---- | :------ | :------ |