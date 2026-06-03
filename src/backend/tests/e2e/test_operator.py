from __future__ import annotations

import pytest

from participium.models.enums import ReportStatus

pytestmark = pytest.mark.e2e


def test_pending_reports_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/operator/reports/pending")
    assert response.status_code == 401


def test_pending_reports_returns_403_for_citizen(citizen_client):
    response = citizen_client.get("/api/v1/operator/reports/pending")
    assert response.status_code == 403


def test_pending_reports_operator_sees_only_own_category(
    operator_client, operator_category, make_category, make_report
):
    """Operator is filtered to their assigned category."""
    other_cat = make_category(name="Other Category")
    r_mine = make_report(category_id=operator_category.id, status=ReportStatus.PENDING_APPROVAL)
    r_other = make_report(category_id=other_cat.id, status=ReportStatus.PENDING_APPROVAL)

    response = operator_client.get("/api/v1/operator/reports/pending")
    assert response.status_code == 200
    ids = [r["id"] for r in response.get_json()]
    assert r_mine.id in ids
    assert r_other.id not in ids


def test_pending_reports_excludes_non_pending_statuses(
    operator_client, operator_category, make_report
):
    make_report(category_id=operator_category.id, status=ReportStatus.PENDING_APPROVAL)
    make_report(category_id=operator_category.id, status=ReportStatus.RESOLVED)

    response = operator_client.get("/api/v1/operator/reports/pending")
    assert response.status_code == 200
    assert all(r["status"] == ReportStatus.PENDING_APPROVAL.value for r in response.get_json())


def test_pending_reports_admin_sees_all_categories(
    admin_client, make_category, make_report
):
    cat_a = make_category(name="Cat A")
    cat_b = make_category(name="Cat B")
    r_a = make_report(category_id=cat_a.id, status=ReportStatus.PENDING_APPROVAL)
    r_b = make_report(category_id=cat_b.id, status=ReportStatus.PENDING_APPROVAL)

    response = admin_client.get("/api/v1/operator/reports/pending")
    assert response.status_code == 200
    ids = [r["id"] for r in response.get_json()]
    assert r_a.id in ids
    assert r_b.id in ids


def test_assigned_reports_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/operator/reports/assigned")
    assert response.status_code == 401


def test_assigned_reports_returns_403_for_citizen(citizen_client):
    response = citizen_client.get("/api/v1/operator/reports/assigned")
    assert response.status_code == 403


def test_assigned_reports_returns_200_for_operator(operator_client, operator_category, make_report):
    make_report(category_id=operator_category.id, status=ReportStatus.ASSIGNED)
    response = operator_client.get("/api/v1/operator/reports/assigned")
    assert response.status_code == 200


def test_assigned_reports_includes_unread_message_count_field(
    operator_client, operator_category, make_report
):
    make_report(category_id=operator_category.id, status=ReportStatus.ASSIGNED)
    response = operator_client.get("/api/v1/operator/reports/assigned")
    assert response.status_code == 200
    for item in response.get_json():
        assert "unread_message_count" in item



def test_assign_report_returns_401_when_unauthenticated(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    response = client.post(f"/api/v1/operator/reports/{report.id}/assign")
    assert response.status_code == 401


def test_assign_report_returns_403_for_citizen(citizen_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    response = citizen_client.post(f"/api/v1/operator/reports/{report.id}/assign")
    assert response.status_code == 403


def test_operator_can_assign_report_in_own_category(
    operator_client, operator_category, make_report
):
    report = make_report(
        category_id=operator_category.id,
        status=ReportStatus.PENDING_APPROVAL,
    )
    response = operator_client.post(f"/api/v1/operator/reports/{report.id}/assign")
    assert response.status_code == 200
    assert response.get_json()["status"] == ReportStatus.ASSIGNED.value


def test_admin_can_assign_any_report(admin_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    response = admin_client.post(f"/api/v1/operator/reports/{report.id}/assign")
    assert response.status_code == 200


def test_assign_report_returns_404_for_unknown(operator_client):
    response = operator_client.post("/api/v1/operator/reports/9999/assign")
    assert response.status_code == 404



def test_update_status_returns_401_when_unauthenticated(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    response = client.post(f"/api/v1/operator/reports/{report.id}/status", json={"status": "in_progress"})
    assert response.status_code == 401


def test_update_status_returns_403_for_citizen(citizen_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    response = citizen_client.post(f"/api/v1/operator/reports/{report.id}/status", json={"status": "in_progress"})
    assert response.status_code == 403


def test_operator_can_advance_status_to_in_progress(
    operator_client, operator_category, make_report
):
    report = make_report(category_id=operator_category.id, status=ReportStatus.ASSIGNED)
    response = operator_client.post(
        f"/api/v1/operator/reports/{report.id}/status",
        json={"status": ReportStatus.IN_PROGRESS.value, "note": "Working on it."},
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == ReportStatus.IN_PROGRESS.value


def test_operator_can_advance_status_to_resolved(
    operator_client, operator_category, make_report
):
    report = make_report(category_id=operator_category.id, status=ReportStatus.IN_PROGRESS)
    response = operator_client.post(
        f"/api/v1/operator/reports/{report.id}/status",
        json={"status": ReportStatus.RESOLVED.value},
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == ReportStatus.RESOLVED.value


def test_update_status_returns_400_for_invalid_transition(
    operator_client, operator_category, make_report
):
    """Operator cannot jump from PENDING directly to RESOLVED."""
    report = make_report(category_id=operator_category.id, status=ReportStatus.PENDING_APPROVAL)
    response = operator_client.post(
        f"/api/v1/operator/reports/{report.id}/status",
        json={"status": ReportStatus.RESOLVED.value},
    )
    assert response.status_code == 400


def test_update_status_returns_400_for_unknown_status_value(
    operator_client, operator_category, make_report
):
    report = make_report(category_id=operator_category.id, status=ReportStatus.ASSIGNED)
    response = operator_client.post(
        f"/api/v1/operator/reports/{report.id}/status",
        json={"status": "warp_speed"},
    )
    assert response.status_code == 400