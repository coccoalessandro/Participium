from __future__ import annotations

import pytest

PASSWORD = "Password1!"

pytestmark = pytest.mark.e2e

_REGISTER_BASE = {
    "first_name": "Test",
    "last_name": "User",
    "password": PASSWORD,
}


def _register(client, username: str, email: str, **kwargs):
    return client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, **_REGISTER_BASE, **kwargs},
    )


def test_register_returns_201_and_user_payload(client):
    response = _register(client, "newuser", "newuser@example.com")
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"


def test_register_exposes_verification_url(client):
    response = _register(client, "toverify", "toverify@example.com")
    assert response.status_code == 201
    assert "verification_url" in response.get_json()


def test_register_returns_400_when_username_missing(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "nouser@example.com",
        "password": PASSWORD,
        "first_name": "Test",
        "last_name": "User",
    })
    assert response.status_code == 400


def test_register_returns_400_when_email_missing(client):
    response = client.post("/api/v1/auth/register", json={
        "username": "noemail",
        "password": PASSWORD,
        "first_name": "Test",
        "last_name": "User",
    })
    assert response.status_code == 400


def test_register_returns_400_when_username_already_taken(client, make_user):
    make_user(username="taken")
    response = _register(client, "taken", "unique@example.com")
    assert response.status_code == 400


def test_register_returns_400_when_email_already_taken(client, make_user):
    make_user(email="dup@example.com")
    response = _register(client, "unique_user", "dup@example.com")
    assert response.status_code == 400


def test_verify_email_returns_200_and_marks_user_verified(client):
    reg_response = _register(client, "unverified", "unverified@example.com")
    verification_url = reg_response.get_json().get("verification_url", "")
    token = verification_url.rstrip("/").split("/")[-1]

    response = client.get(f"/api/v1/auth/verify/{token}")
    assert response.status_code == 200
    assert response.get_json()["user"]["is_email_verified"] is True


def test_verify_email_returns_400_for_invalid_token(client):
    response = client.get("/api/v1/auth/verify/not-a-real-token")
    assert response.status_code == 400


def test_verify_email_returns_400_for_already_used_token(client):
    reg_response = _register(client, "doubleverify", "doubleverify@example.com")
    token = reg_response.get_json()["verification_url"].rstrip("/").split("/")[-1]

    client.get(f"/api/v1/auth/verify/{token}")
    second = client.get(f"/api/v1/auth/verify/{token}")
    assert second.status_code == 400


def test_login_returns_200_and_user_for_valid_credentials(client, citizen):
    response = client.post("/api/v1/auth/login", json={
        "identifier": citizen.username,
        "password": PASSWORD,
    })
    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == citizen.username


def test_login_also_works_with_email_as_identifier(client, citizen):
    response = client.post("/api/v1/auth/login", json={
        "identifier": citizen.email,
        "password": PASSWORD,
    })
    assert response.status_code == 200


def test_login_returns_401_for_wrong_password(client, citizen):
    response = client.post("/api/v1/auth/login", json={
        "identifier": citizen.username,
        "password": "wrong_password",
    })
    assert response.status_code == 401


def test_login_returns_401_for_unknown_identifier(client):
    response = client.post("/api/v1/auth/login", json={
        "identifier": "nobody",
        "password": PASSWORD,
    })
    assert response.status_code == 401


def test_login_returns_401_for_inactive_user(client, make_user):
    make_user(username="inactive", email="inactive@example.com", is_active=False)
    response = client.post("/api/v1/auth/login", json={
        "identifier": "inactive",
        "password": PASSWORD,
    })
    assert response.status_code == 401


def test_login_sets_session_allowing_protected_endpoint(client, citizen):
    client.post("/api/v1/auth/login", json={"identifier": citizen.username, "password": PASSWORD})
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200


def test_logout_returns_200(citizen_client):
    response = citizen_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Logged out."


def test_logout_clears_session(citizen_client):
    citizen_client.post("/api/v1/auth/logout")
    response = citizen_client.get("/api/v1/users/me")
    assert response.status_code == 401



def _register(client, username: str, email: str, **kwargs):
    return client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, **_REGISTER_BASE, **kwargs},
    )


def test_register_returns_201_and_user_payload(client):
    response = _register(client, "newuser", "newuser@example.com")
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"


def test_register_exposes_verification_url(client):
    response = _register(client, "toverify", "toverify@example.com")
    assert response.status_code == 201
    assert "verification_url" in response.get_json()


def test_register_hides_verification_link_when_configured(client):
    original_setting = client.application.config["SETTINGS"].expose_verification_links
    
    try:
        client.application.config["SETTINGS"].expose_verification_links = False
        
        response = _register(client, "hiddenlink", "hidden@example.com")
        
        assert response.status_code == 201
        data = response.get_json()
        assert "user" in data
        assert "verification_url" not in data  

    finally:
        client.application.config["SETTINGS"].expose_verification_links = original_setting