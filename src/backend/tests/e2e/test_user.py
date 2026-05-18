from __future__ import annotations

import pytest

from participium.models.enums import Role

pytestmark = pytest.mark.e2e


def test_me_returns_current_user_profile(citizen_client, citizen):
    response = citizen_client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == citizen.username
    assert data["email"] == citizen.email


def test_me_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_update_me_changes_username(citizen_client):
    response = citizen_client.put("/api/v1/users/me", json={"username": "citizen_v2"})
    assert response.status_code == 200
    assert response.get_json()["username"] == "citizen_v2"


def test_update_me_changes_first_and_last_name(citizen_client):
    response = citizen_client.put("/api/v1/users/me", json={
        "first_name": "Updated",
        "last_name": "Name",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


def test_update_me_returns_400_for_duplicate_username(citizen_client, make_user):
    make_user(username="already_taken")
    response = citizen_client.put("/api/v1/users/me", json={"username": "already_taken"})
    assert response.status_code == 400


def test_update_me_returns_401_when_unauthenticated(client):
    response = client.put("/api/v1/users/me", json={"username": "ghost"})
    assert response.status_code == 401



def test_delete_me_returns_200_and_success_message(citizen_client):
    response = citizen_client.delete("/api/v1/users/me")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Account deleted."


def test_delete_me_clears_session(citizen_client):
    citizen_client.delete("/api/v1/users/me")
    response = citizen_client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_delete_me_returns_401_when_unauthenticated(client):
    response = client.delete("/api/v1/users/me")
    assert response.status_code == 401



def test_list_notifications_returns_empty_initially(citizen_client):
    response = citizen_client.get("/api/v1/users/me/notifications")
    assert response.status_code == 200
    assert response.get_json() == []


def test_list_notifications_returns_401_when_unauthenticated(client):
    response = client.get("/api/v1/users/me/notifications")
    assert response.status_code == 401



def test_mark_notification_read_returns_404_for_unknown(citizen_client):
    response = citizen_client.post("/api/v1/users/me/notifications/9999/read")
    assert response.status_code == 404


def test_mark_notification_read_returns_401_when_unauthenticated(client):
    response = client.post("/api/v1/users/me/notifications/1/read")
    assert response.status_code == 401

def test_update_me_email_notifications_as_none(citizen_client):
    response = citizen_client.put("/api/v1/users/me", json={"email_notifications_enabled": None})
    assert response.status_code == 200
    assert response.get_json()["email_notifications_enabled"] is False

def test_update_me_email_notifications_as_string(citizen_client):
    response = citizen_client.put("/api/v1/users/me", json={"email_notifications_enabled": "true"})
    assert response.status_code == 200
    assert response.get_json()["email_notifications_enabled"] is True


def test_update_me_via_form_data_sets_email_notifications_when_present(citizen_client):
    response = citizen_client.put(
        "/api/v1/users/me",
        data={"email_notifications_enabled": "on"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["email_notifications_enabled"] is True

def test_mark_notification_read_returns_200_for_own_notification(
    citizen_client, citizen, make_notification
):
    notif = make_notification(user_id=citizen.id)
    response = citizen_client.post(f"/api/v1/users/me/notifications/{notif.id}/read")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == notif.id
    assert data["is_read"] is True


def test_list_users_returns_200_for_admin(admin_client):
    response = admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200


def test_create_user_returns_201_for_admin(admin_client):
    response = admin_client.post("/api/v1/admin/users", json={
        "username": "new_op",
        "email": "newop@example.com",
        "password": "Password1!",
        "first_name": "New",
        "last_name": "Op",
        "role": Role.CITIZEN.value,
    })
    assert response.status_code == 201


def test_update_user_returns_200_for_admin(admin_client, citizen):
    response = admin_client.put(f"/api/v1/admin/users/{citizen.id}", json={
        "first_name": "Updated",
    })
    assert response.status_code == 200