from __future__ import annotations

from participium.core.status_flow import ensure_transition_allowed

# Function: 
# Inputs: current_status (ReportStatus), next_status (ReportStatus)
# Expected Output:
# - `True` when the transition is allowed, including self-transitions. Allowed transitions:
# -- Pending Approval -> Pending Approval, Assigned, Rejected
# -- Assigned -> Assigned, In Progress, Suspended, Resolved
# -- In Progress -> In Progress, Suspended, Resolved
# -- Suspended -> Suspended, In Progress, Resolved
# -- Rejected -> Rejected
# -- Resolved -> Resolved
# - ValidationError: if the transition is not allowed by the workflow rules.
#def ensure_transition_allowed(current_status: ReportStatus, next_status: ReportStatus) -> bool
#| TC-ID | current_status | next_status | Input |Expected | Fixture |
#| :---- | :--------------| :---------- | :---- |:------- | :------ |

