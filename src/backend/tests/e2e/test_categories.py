from __future__ import annotations

import pytest

pytestmark = pytest.mark.e2e


def test_list_categories_returns_only_active(client, make_category):
    make_category(name="Active One", is_active=True)
    make_category(name="Inactive One", is_active=False)

    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    names = [c["name"] for c in response.get_json()]
    assert "Active One" in names
    assert "Inactive One" not in names


def test_list_categories_returns_empty_when_no_active_categories(client, make_category):
    make_category(name="Gone", is_active=False)
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_categories_accessible_without_auth(client, make_category):
    make_category(name="Public Cat")
    response = client.get("/api/v1/categories")
    assert response.status_code == 200


def test_admin_list_categories_returns_all_including_inactive(admin_client, make_category):
    make_category(name="Active", is_active=True)
    make_category(name="Inactive", is_active=False)

    response = admin_client.get("/api/v1/admin/categories")
    assert response.status_code == 200
    names = [c["name"] for c in response.get_json()]
    assert "Active" in names
    assert "Inactive" in names


def test_admin_list_categories_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/admin/categories")
    assert response.status_code == 401


def test_admin_list_categories_returns_403_for_citizen(citizen_client):
    response = citizen_client.get("/api/v1/admin/categories")
    assert response.status_code == 403


def test_admin_list_categories_returns_403_for_operator(operator_client):
    response = operator_client.get("/api/v1/admin/categories")
    assert response.status_code == 403


def test_create_category_returns_201_and_category(admin_client):
    response = admin_client.post("/api/v1/admin/categories", json={"name": "New Category"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "New Category"
    assert data["is_active"] is True


def test_create_category_returns_400_for_empty_name(admin_client):
    response = admin_client.post("/api/v1/admin/categories", json={"name": ""})
    assert response.status_code == 400


def test_create_category_returns_400_for_duplicate_name(admin_client, make_category):
    make_category(name="Duplicate")
    response = admin_client.post("/api/v1/admin/categories", json={"name": "Duplicate"})
    assert response.status_code == 400


def test_create_category_returns_403_for_non_admin(citizen_client):
    response = citizen_client.post("/api/v1/admin/categories", json={"name": "X"})
    assert response.status_code == 403


def test_update_category_name(admin_client, make_category):
    cat = make_category(name="Old Name")
    response = admin_client.put(f"/api/v1/admin/categories/{cat.id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.get_json()["name"] == "New Name"


def test_update_category_deactivation(admin_client, make_category):
    cat = make_category(name="Active Cat", is_active=True)
    response = admin_client.put(f"/api/v1/admin/categories/{cat.id}", json={"is_active": False})
    assert response.status_code == 200
    assert response.get_json()["is_active"] is False


def test_update_category_reactivation(admin_client, make_category):
    cat = make_category(name="Dormant", is_active=False)
    response = admin_client.put(f"/api/v1/admin/categories/{cat.id}", json={"is_active": True})
    assert response.status_code == 200
    assert response.get_json()["is_active"] is True


def test_update_category_returns_404_for_unknown_id(admin_client):
    response = admin_client.put("/api/v1/admin/categories/9999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_update_category_returns_403_for_citizen(citizen_client, make_category):
    cat = make_category(name="Protected")
    response = citizen_client.put(f"/api/v1/admin/categories/{cat.id}", json={"name": "Nope"})
    assert response.status_code == 403