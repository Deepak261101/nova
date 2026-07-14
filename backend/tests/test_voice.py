from __future__ import annotations

import base64
import json

from fastapi.testclient import TestClient


def test_synthesize_and_transcribe(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = auth_client

    synth = client.post("/voice/synthesize", headers=headers, json={"text": "hello world"})
    assert synth.status_code == 200
    audio = base64.b64decode(synth.json()["audio_b64"])
    assert audio[:4] == b"RIFF"  # valid WAV header

    files = {"file": ("audio.bin", b"open the terminal", "application/octet-stream")}
    tr = client.post("/voice/transcribe", headers=headers, files=files)
    assert tr.status_code == 200
    assert tr.json()["transcript"] == "open the terminal"


def test_voice_websocket_text_turn(auth_client: tuple[TestClient, dict[str, str]]) -> None:
    client, headers = auth_client
    token = headers["Authorization"].split(" ", 1)[1]
    convo_id = client.post("/conversations", headers=headers, json={}).json()["id"]

    with client.websocket_connect(f"/ws/voice?token={token}") as ws:
        ws.send_text(json.dumps({"type": "text", "conversation_id": convo_id, "text": "Hi Nova"}))
        seen = {"transcript": None, "reply": None, "audio": None}
        while not all(seen.values()):
            msg = json.loads(ws.receive_text())
            if msg["type"] in seen:
                seen[msg["type"]] = msg

    assert seen["transcript"]["text"] == "Hi Nova"
    assert "Hi Nova" in seen["reply"]["text"]
    assert seen["audio"]["mime"] == "audio/wav"


def test_voice_websocket_rejects_bad_token(client: TestClient) -> None:
    with client.websocket_connect("/ws/voice?token=bogus") as ws:
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
        assert msg["detail"] == "unauthorized"
