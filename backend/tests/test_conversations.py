from __future__ import annotations

from fastapi.testclient import TestClient


def test_conversation_flow(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = auth_client

    created = client.post("/conversations", headers=headers, json={"title": "New conversation"})
    assert created.status_code == 201, created.text
    convo_id = created.json()["id"]

    listed = client.get("/conversations", headers=headers)
    assert listed.status_code == 200
    assert any(c["id"] == convo_id for c in listed.json())

    reply = client.post(
        f"/conversations/{convo_id}/messages",
        headers=headers,
        json={"message": "Hello Nova"},
    )
    assert reply.status_code == 200, reply.text
    assert reply.json()["role"] == "assistant"
    assert "Hello Nova" in reply.json()["content"]

    detail = client.get(f"/conversations/{convo_id}", headers=headers)
    assert detail.status_code == 200
    roles = [m["role"] for m in detail.json()["messages"]]
    assert roles == ["user", "assistant"]
    # Auto-title uses the first user message.
    assert detail.json()["title"] == "Hello Nova"


def test_streaming_chat(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = auth_client
    convo_id = client.post("/conversations", headers=headers, json={}).json()["id"]

    with client.stream(
        "POST",
        f"/conversations/{convo_id}/stream",
        headers=headers,
        json={"message": "Stream please"},
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())
    assert "data:" in body


def test_cannot_access_others_conversation(client: TestClient) -> None:
    a = client.post(
        "/auth/register", json={"email": "a@ex.com", "password": "password12345"}
    ).json()["tokens"]["access_token"]
    b = client.post(
        "/auth/register", json={"email": "b@ex.com", "password": "password12345"}
    ).json()["tokens"]["access_token"]

    convo_id = client.post(
        "/conversations", headers={"Authorization": f"Bearer {a}"}, json={}
    ).json()["id"]

    resp = client.get(f"/conversations/{convo_id}", headers={"Authorization": f"Bearer {b}"})
    assert resp.status_code == 404
