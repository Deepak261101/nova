from __future__ import annotations

from fastapi.testclient import TestClient


def test_memory_crud(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = auth_client

    put = client.put(
        "/memory", headers=headers, json={"key": "name", "value": "Alice", "importance": 5}
    )
    assert put.status_code == 200
    assert put.json()["value"] == "Alice"

    listed = client.get("/memory", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["key"] == "name"

    deleted = client.delete("/memory/name", headers=headers)
    assert deleted.status_code == 204
    assert client.get("/memory", headers=headers).json() == []


def test_update_profile_and_settings(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = auth_client

    prof = client.patch("/users/me", headers=headers, json={"display_name": "Alice B"})
    assert prof.status_code == 200
    assert prof.json()["display_name"] == "Alice B"

    settings = client.put(
        "/users/me/settings", headers=headers, json={"settings": {"theme": "dark"}}
    )
    assert settings.status_code == 200
    assert settings.json()["settings"]["theme"] == "dark"


def test_health_and_ready(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["status"] == "ready"
