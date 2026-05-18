from __future__ import annotations

import pytest

from participium.models.enums import ReportStatus

pytestmark = pytest.mark.e2e


def test_list_messages_returns_401_when_unauthenticated(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    response = client.get(f"/api/v1/reports/{report.id}/messages")
    assert response.status_code == 401


def test_list_messages_returns_403_for_citizen_not_owning_report(
    citizen_client, make_category, make_report
):
    """A citizen who is not the reporter cannot access the thread."""
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED, reporter_id=None)
    response = citizen_client.get(f"/api/v1/reports/{report.id}/messages")
    assert response.status_code == 403


def test_list_messages_returns_200_for_report_owner(
    citizen_client, make_category, make_report, citizen
):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED, reporter_id=citizen.id)
    response = citizen_client.get(f"/api/v1/reports/{report.id}/messages")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_list_messages_returns_200_for_operator(
    operator_client, operator_category, make_report
):
    report = make_report(category_id=operator_category.id, status=ReportStatus.ASSIGNED)
    response = operator_client.get(f"/api/v1/reports/{report.id}/messages")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_list_messages_returns_200_for_admin(admin_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    response = admin_client.get(f"/api/v1/reports/{report.id}/messages")
    assert response.status_code == 200


def test_send_message_returns_401_when_unauthenticated(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    response = client.post(f"/api/v1/reports/{report.id}/messages", json={"body": "Hello"})
    assert response.status_code == 401


def test_send_message_returns_403_for_citizen_not_owning_report(
    citizen_client, make_category, make_report
):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED, reporter_id=None)
    response = citizen_client.post(
        f"/api/v1/reports/{report.id}/messages", json={"body": "Sneak"}
    )
    assert response.status_code == 403


def test_citizen_can_send_message_on_own_report(
    citizen_client, operator_client, operator_category, make_report, citizen
):
    report = make_report(category_id=operator_category.id, status=ReportStatus.PENDING_APPROVAL, reporter_id=citizen.id)
    
    
    operator_client.post(f"/api/v1/operator/reports/{report.id}/assign")
    
    response = citizen_client.post(
        f"/api/v1/reports/{report.id}/messages",
        json={"body": "Any update?"},
    )
    
    assert response.status_code == 201

def test_operator_can_send_message_on_assigned_report(
    operator_client, operator_category, make_report, citizen
):
    
    report = make_report(category_id=operator_category.id, status=ReportStatus.PENDING_APPROVAL, reporter_id=citizen.id)
    
    operator_client.post(f"/api/v1/operator/reports/{report.id}/assign")
    
    response = operator_client.post(
        f"/api/v1/reports/{report.id}/messages",
        json={"body": "We are looking into it."},
    )
    
    assert response.status_code == 201
    assert response.get_json()["body"] == "We are looking into it."

def test_send_message_returns_400_for_empty_body(
    citizen_client, make_category, make_report, citizen
):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED, reporter_id=citizen.id)
    response = citizen_client.post(
        f"/api/v1/reports/{report.id}/messages",
        json={"body": ""},
    )
    assert response.status_code == 400


def test_sent_message_appears_in_list(
    citizen_client, operator_client, operator_category, make_report, citizen
):
    report = make_report(category_id=operator_category.id, status=ReportStatus.PENDING_APPROVAL, reporter_id=citizen.id)
    operator_client.post(f"/api/v1/operator/reports/{report.id}/assign")
    
    citizen_client.post(
        f"/api/v1/reports/{report.id}/messages",
        json={"body": "Visible message"},
    )
    
    list_response = citizen_client.get(f"/api/v1/reports/{report.id}/messages")
    bodies = [m["body"] for m in list_response.get_json()]
    assert "Visible message" in bodies