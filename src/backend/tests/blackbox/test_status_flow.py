from __future__ import annotations

from participium.core.status_flow import ensure_transition_allowed

from participium.models.enums import ReportStatus
from participium.core.exceptions import ValidationError
import pytest

# Function: ensure_transition_allowed
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


@pytest.mark.parametrize(
    "current_status, next_status",
    [
        # TC-1
        (ReportStatus.PENDING_APPROVAL, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.ASSIGNED),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.REJECTED),
        
        # TC-3
        (ReportStatus.ASSIGNED, ReportStatus.ASSIGNED),
        (ReportStatus.ASSIGNED, ReportStatus.IN_PROGRESS),
        (ReportStatus.ASSIGNED, ReportStatus.SUSPENDED),
        (ReportStatus.ASSIGNED, ReportStatus.RESOLVED),
        
        # TC-5
        (ReportStatus.IN_PROGRESS, ReportStatus.IN_PROGRESS),
        (ReportStatus.IN_PROGRESS, ReportStatus.SUSPENDED),
        (ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED),
        
        # TC-7
        (ReportStatus.SUSPENDED, ReportStatus.SUSPENDED),
        (ReportStatus.SUSPENDED, ReportStatus.IN_PROGRESS),
        (ReportStatus.SUSPENDED, ReportStatus.RESOLVED),
        
        # TC-9
        (ReportStatus.REJECTED, ReportStatus.REJECTED),
        
        # TC-11
        (ReportStatus.RESOLVED, ReportStatus.RESOLVED),
    ]
)
def test_ensure_transition_allowed_success(current_status: ReportStatus, next_status: ReportStatus) -> None:
    result_value = ensure_transition_allowed(current_status, next_status)
    assert result_value is True


@pytest.mark.parametrize(
    "current_status, next_status",
    [
        # TC-2
        (ReportStatus.PENDING_APPROVAL, ReportStatus.IN_PROGRESS),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.SUSPENDED),
        (ReportStatus.PENDING_APPROVAL, ReportStatus.RESOLVED),
        
        # TC-4
        (ReportStatus.ASSIGNED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.ASSIGNED, ReportStatus.REJECTED),
        
        # TC-6
        (ReportStatus.IN_PROGRESS, ReportStatus.REJECTED),
        (ReportStatus.IN_PROGRESS, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.IN_PROGRESS, ReportStatus.ASSIGNED),
        
        # TC-8
        (ReportStatus.SUSPENDED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.SUSPENDED, ReportStatus.ASSIGNED),
        (ReportStatus.SUSPENDED, ReportStatus.REJECTED),
        
        # TC-10
        (ReportStatus.REJECTED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.REJECTED, ReportStatus.ASSIGNED),
        (ReportStatus.REJECTED, ReportStatus.IN_PROGRESS),
        (ReportStatus.REJECTED, ReportStatus.SUSPENDED),
        (ReportStatus.REJECTED, ReportStatus.RESOLVED),
        
        # TC-12
        (ReportStatus.RESOLVED, ReportStatus.PENDING_APPROVAL),
        (ReportStatus.RESOLVED, ReportStatus.ASSIGNED),
        (ReportStatus.RESOLVED, ReportStatus.IN_PROGRESS),
        (ReportStatus.RESOLVED, ReportStatus.SUSPENDED),
        (ReportStatus.RESOLVED, ReportStatus.REJECTED),
    ]
)
def test_ensure_transition_allowed_raises_validation_error(current_status: ReportStatus, next_status: ReportStatus) -> None:
    with pytest.raises(ValidationError):
        ensure_transition_allowed(current_status, next_status)