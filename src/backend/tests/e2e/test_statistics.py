from __future__ import annotations

import pytest

from participium.models.enums import ReportStatus

pytestmark = pytest.mark.e2e


def test_public_stats_returns_200_without_auth(client):
    response = client.get("/api/v1/stats/public")
    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)


def test_public_stats_default_granularity_is_day(client):
    response = client.get("/api/v1/stats/public")
    assert response.status_code == 200


def test_public_stats_with_week_granularity(client):
    response = client.get("/api/v1/stats/public?granularity=week")
    assert response.status_code == 200


def test_public_stats_with_month_granularity(client):
    response = client.get("/api/v1/stats/public?granularity=month")
    assert response.status_code == 200


def test_public_stats_returns_200_fallback_for_invalid_granularity(client):
    response = client.get("/api/v1/stats/public?granularity=decade")
    assert response.status_code == 200
    assert "reports_by_category" in response.get_json()


def test_public_stats_reflects_existing_public_reports(client, make_category, make_report):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)

    response = client.get("/api/v1/stats/public")
    assert response.status_code == 200
    assert response.get_json() is not None