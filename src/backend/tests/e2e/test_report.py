from __future__ import annotations

import pytest

import io

from participium.models.enums import ReportStatus

pytestmark = pytest.mark.e2e


def test_list_public_reports_excludes_pending_and_rejected(client, make_category, make_report):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    make_report(category_id=cat.id, status=ReportStatus.REJECTED)
    r_public = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)

    response = client.get("/api/v1/reports")
    assert response.status_code == 200
    ids = [r["id"] for r in response.get_json()]
    assert r_public.id in ids
    assert len([r for r in response.get_json()
                if r["status"] in ("pending_approval", "rejected")]) == 0


def test_list_public_reports_includes_assigned_and_in_progress(client, make_category, make_report):
    cat = make_category()
    r_assigned = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    r_in_progress = make_report(category_id=cat.id, status=ReportStatus.IN_PROGRESS)

    response = client.get("/api/v1/reports")
    ids = [r["id"] for r in response.get_json()]
    assert r_assigned.id in ids
    assert r_in_progress.id in ids


def test_list_public_reports_filters_by_category(client, make_category, make_report):
    cat_a = make_category(name="Roads")
    cat_b = make_category(name="Waste")
    r_a = make_report(category_id=cat_a.id, status=ReportStatus.RESOLVED)
    make_report(category_id=cat_b.id, status=ReportStatus.RESOLVED)

    response = client.get(f"/api/v1/reports?category_id={cat_a.id}")
    assert response.status_code == 200
    ids = [r["id"] for r in response.get_json()]
    assert r_a.id in ids
    assert len(ids) == 1


def test_list_public_reports_filters_by_status(client, make_category, make_report):
    cat = make_category()
    r_resolved = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)

    response = client.get(f"/api/v1/reports?status={ReportStatus.RESOLVED.value}")
    assert response.status_code == 200
    ids = [r["id"] for r in response.get_json()]
    assert r_resolved.id in ids
    assert len(ids) == 1


def test_list_public_reports_returns_400_for_invalid_status(client):
    response = client.get("/api/v1/reports?status=flying_saucer")
    assert response.status_code == 400


def test_list_public_reports_sort_asc_returns_oldest_first(client, make_category, make_report):
    cat = make_category()
    r_old = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    r_new = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)

    response = client.get("/api/v1/reports?sort=asc")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["id"] == r_old.id
    assert data[1]["id"] == r_new.id


def test_list_public_reports_accessible_without_auth(client, make_category, make_report):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    response = client.get("/api/v1/reports")
    assert response.status_code == 200


def test_report_detail_returns_200_for_public_report(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)

    response = client.get(f"/api/v1/reports/{report.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == report.id
    assert data["title"] == report.title


def test_report_detail_returns_403_for_pending_when_unauthenticated(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)

    response = client.get(f"/api/v1/reports/{report.id}")
    assert response.status_code == 403


def test_report_detail_returns_200_for_pending_when_admin(admin_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)

    response = admin_client.get(f"/api/v1/reports/{report.id}")
    assert response.status_code == 200


def test_report_detail_returns_404_for_unknown_report(client):
    response = client.get("/api/v1/reports/99999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_export_returns_csv_content_type(client, make_category, make_report):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)

    response = client.get("/api/v1/reports/export")
    assert response.status_code == 200
    assert "text/csv" in response.content_type


def test_export_returns_csv_with_headers_row(client, make_category, make_report):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)

    response = client.get("/api/v1/reports/export")
    content = response.data.decode()
    first_line = content.splitlines()[0]
    assert "id" in first_line
    assert "title" in first_line


def test_export_returns_empty_csv_when_no_public_reports(client):
    response = client.get("/api/v1/reports/export")
    assert response.status_code == 200


def test_create_report_returns_401_when_unauthenticated(client):
    response = client.post("/api/v1/reports", data={})
    assert response.status_code == 401


def test_create_report_returns_403_for_operator(operator_client, make_category):
    cat = make_category()
    response = operator_client.post("/api/v1/reports", data={
        "title": "Test",
        "description": "Desc",
        "category_id": str(cat.id),
        "latitude": "45.0",
        "longitude": "9.0",
    })
    assert response.status_code == 403


def test_create_report_returns_403_for_admin(admin_client, make_category):
    cat = make_category()
    response = admin_client.post("/api/v1/reports", data={
        "title": "Test",
        "description": "Desc",
        "category_id": str(cat.id),
        "latitude": "45.0",
        "longitude": "9.0",
    })
    assert response.status_code == 403


def test_follow_returns_401_when_unauthenticated(client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    response = client.post(f"/api/v1/reports/{report.id}/follow")
    assert response.status_code == 401


def test_follow_returns_403_for_operator(operator_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    response = operator_client.post(f"/api/v1/reports/{report.id}/follow")
    assert response.status_code == 403


def test_citizen_can_follow_a_public_report(citizen_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    response = citizen_client.post(f"/api/v1/reports/{report.id}/follow")
    assert response.status_code == 200


def test_citizen_can_unfollow_a_followed_report(citizen_client, make_category, make_report):
    cat = make_category()
    report = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    citizen_client.post(f"/api/v1/reports/{report.id}/follow")

    response = citizen_client.delete(f"/api/v1/reports/{report.id}/follow")
    assert response.status_code == 200


def test_my_reports_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/users/me/reports")
    assert response.status_code == 401


def test_my_reports_returns_citizen_own_reports(citizen_client, make_category, make_report, citizen):
    cat = make_category()
    my_report = make_report(category_id=cat.id, reporter_id=citizen.id)
    other = make_report(category_id=cat.id, reporter_id=None)

    response = citizen_client.get("/api/v1/users/me/reports")
    assert response.status_code == 200
    ids = [r["id"] for r in response.get_json()]
    assert my_report.id in ids
    assert other.id not in ids


def test_my_reports_returns_empty_when_user_has_no_reports(citizen_client):
    response = citizen_client.get("/api/v1/users/me/reports")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_report_returns_201_for_citizen(citizen_client, make_category):
    cat = make_category()
    photo = (io.BytesIO(b"fake image content"), "photo.jpg")

    response = citizen_client.post(
        "/api/v1/reports",
        data={
            "title": "Buca in strada",
            "description": "Una buca pericolosa",
            "category_id": str(cat.id),
            "latitude": "45.0",
            "longitude": "9.0",
            "photos": photo,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Buca in strada"


def test_create_report_anonymous_returns_201(citizen_client, make_category):
    cat = make_category()
    photo = (io.BytesIO(b"fake image content"), "photo.jpg")

    response = citizen_client.post(
        "/api/v1/reports",
        data={
            "title": "Segnalazione anonima",
            "description": "Descrizione",
            "category_id": str(cat.id),
            "latitude": "45.1",
            "longitude": "9.1",
            "is_anonymous": "true",
            "photos": photo,
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    assert response.get_json()["is_anonymous"] is True