from __future__ import annotations

import pytest

from participium.models.enums import ReportStatus, Role

pytestmark = pytest.mark.e2e


def test_health_check_returns_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_reference_data_contains_roles(client):
    response = client.get("/api/v1/meta/reference-data")
    assert response.status_code == 200
    data = response.get_json()
    assert "roles" in data
    for role in Role:
        assert role.value in data["roles"]


def test_reference_data_contains_report_statuses(client):
    response = client.get("/api/v1/meta/reference-data")
    data = response.get_json()
    assert "report_statuses" in data
    for status in ReportStatus:
        assert status.value in data["report_statuses"]


def test_reference_data_contains_public_statuses_subset(client):
    response = client.get("/api/v1/meta/reference-data")
    data = response.get_json()
    assert "public_report_statuses" in data
    assert set(data["public_report_statuses"]).issubset(set(data["report_statuses"]))
    assert "pending_approval" not in data["public_report_statuses"]
    assert "rejected" not in data["public_report_statuses"]


def test_unknown_route_returns_404(client):
    response = client.get("/api/v1/does_not_exist")
    assert response.status_code == 404
    assert "error" in response.get_json()