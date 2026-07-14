from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_and_me(client: TestClient) -> None:
    resp = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "password12345", "display_name": "Bob"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["user"]["email"] == "bob@example.com"
    token = body["tokens"]["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["display_name"] == "Bob"


def test_duplicate_registration_conflicts(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "password12345"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_and_refresh(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "password12345"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "carol@example.com", "password": "password12345"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["tokens"]["refresh_token"]

    refreshed = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


def test_login_wrong_password(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "dave@example.com", "password": "password12345"},
    )
    resp = client.post(
        "/auth/login",
        json={"email": "dave@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401
