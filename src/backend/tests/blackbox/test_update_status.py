from __future__ import annotations

from participium.services.report_service import ReportService

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
#| TC-ID | report_id | operator | next_status_value | note | Input |Expected | Fixture |
#| :---- | :-------- | :------- | :---------------- |:-----| :---- |:--------| :------ |
