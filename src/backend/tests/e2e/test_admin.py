from __future__ import annotations

import pytest

from participium.models.enums import Role

pytestmark = pytest.mark.e2e

def test_list_users_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401


def test_list_users_returns_403_for_citizen(citizen_client):
    response = citizen_client.get("/api/v1/admin/users")
    assert response.status_code == 403


def test_list_users_returns_403_for_operator(operator_client):
    response = operator_client.get("/api/v1/admin/users")
    assert response.status_code == 403


def test_list_users_returns_all_registered_users(admin_client, make_user):
    u1 = make_user(username="alpha")
    u2 = make_user(username="beta")

    response = admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    usernames = [u["username"] for u in response.get_json()]
    assert u1.username in usernames
    assert u2.username in usernames

def test_create_user_returns_201_and_new_user(admin_client):
    response = admin_client.post("/api/v1/admin/users", json={
        "username": "newcitizen",
        "first_name": "New",
        "last_name": "Citizen",
        "email": "newcitizen@example.com",
        "password": "Password1!",
        "role": Role.CITIZEN.value,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "newcitizen"
    assert data["role"] == Role.CITIZEN.value


def test_create_operator_user_with_category(admin_client, make_category):
    cat = make_category(name="Infra")
    response = admin_client.post("/api/v1/admin/users", json={
        "username": "newoperator",
        "first_name": "New",
        "last_name": "Op",
        "email": "newoperator@example.com",
        "password": "Password1!",
        "role": Role.OPERATOR.value,
        "category_id": cat.id,
    })
    assert response.status_code == 201
    assert response.get_json()["role"] == Role.OPERATOR.value


def test_create_user_returns_400_for_duplicate_username(admin_client, make_user):
    make_user(username="collision")
    response = admin_client.post("/api/v1/admin/users", json={
        "username": "collision",
        "first_name": "A",
        "last_name": "B",
        "email": "unique@example.com",
        "password": "Password1!",
        "role": Role.CITIZEN.value,
    })
    assert response.status_code == 400


def test_create_user_returns_400_for_duplicate_email(admin_client, make_user):
    make_user(email="dup@example.com")
    response = admin_client.post("/api/v1/admin/users", json={
        "username": "unique_name",
        "first_name": "A",
        "last_name": "B",
        "email": "dup@example.com",
        "password": "Password1!",
        "role": Role.CITIZEN.value,
    })
    assert response.status_code == 400


def test_create_user_returns_403_for_non_admin(citizen_client):
    response = citizen_client.post("/api/v1/admin/users", json={
        "username": "sneak",
        "first_name": "S",
        "last_name": "N",
        "email": "sneak@example.com",
        "password": "Password1!",
        "role": Role.CITIZEN.value,
    })
    assert response.status_code == 403


def test_update_user_deactivates_account(admin_client, make_user):
    user = make_user(username="to_deactivate")
    response = admin_client.put(f"/api/v1/admin/users/{user.id}", json={"is_active": False})
    assert response.status_code == 200
    assert response.get_json()["is_active"] is False


def test_update_user_reactivates_account(admin_client, make_user):
    user = make_user(username="dormant", is_active=False)
    response = admin_client.put(f"/api/v1/admin/users/{user.id}", json={"is_active": True})
    assert response.status_code == 200
    assert response.get_json()["is_active"] is True


def test_update_user_changes_role(admin_client, make_user, make_category):
    cat = make_category(name="Infra")
    user = make_user(username="promote_me", role=Role.CITIZEN)
    response = admin_client.put(f"/api/v1/admin/users/{user.id}", json={
        "role": Role.OPERATOR.value,
        "category_id": cat.id,
    })
    assert response.status_code == 200
    assert response.get_json()["role"] == Role.OPERATOR.value


def test_update_user_returns_404_for_unknown_user(admin_client):
    response = admin_client.put("/api/v1/admin/users/99999", json={"is_active": False})
    assert response.status_code == 404


def test_update_user_returns_403_for_non_admin(citizen_client, make_user):
    user = make_user(username="victim")
    response = citizen_client.put(f"/api/v1/admin/users/{user.id}", json={"is_active": False})
    assert response.status_code == 403


def test_admin_stats_returns_200_and_dict(admin_client):
    response = admin_client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)


def test_admin_stats_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 401


def test_admin_stats_returns_403_for_citizen(citizen_client):
    response = citizen_client.get("/api/v1/admin/stats")
    assert response.status_code == 403


def test_admin_stats_returns_403_for_operator(operator_client):
    response = operator_client.get("/api/v1/admin/stats")
    assert response.status_code == 403