from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Iterator[Settings]:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield Settings(
        env="test",
        debug=False,
        database_url=f"sqlite+aiosqlite:///{path}",
        jwt_secret="test-secret",
        llm_provider="mock",
        stt_provider="mock",
        tts_provider="mock",
        access_token_expire_minutes=30,
    )
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_client(client: TestClient) -> tuple[TestClient, dict[str, str]]:
    resp = client.post(
        "/auth/register",
        json={
            "email": "alice@example.com",
            "password": "supersecret123",
            "display_name": "Alice",
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return client, headers
