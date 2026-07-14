"""Real-time voice websocket.

Protocol (JSON text frames from client):
  {"type": "start", "conversation_id": "..."}   -> optional, sets active convo
  {"type": "audio", "conversation_id": "...", "audio_b64": "..."}  -> a voice turn
  {"type": "text",  "conversation_id": "...", "text": "..."}       -> typed turn

Server emits:
  {"type": "transcript", "text": "..."}
  {"type": "token", "delta": "..."}            (streamed assistant text)
  {"type": "reply", "text": "..."}             (final assistant text)
  {"type": "audio", "audio_b64": "...", "mime": "audio/wav"}
  {"type": "error", "detail": "..."}
"""

from __future__ import annotations

import base64
import contextlib
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.adapters.db.repositories import (
    SqlConversationRepository,
    SqlMemoryRepository,
    SqlUserRepository,
)
from app.core.container import Container
from app.core.exceptions import NovaError
from app.core.logging import get_logger
from app.services.auth import AuthService
from app.services.conversation import ConversationService
from app.services.memory import MemoryService
from app.services.voice import VoiceService

router = APIRouter()
log = get_logger(__name__)


@router.websocket("/ws/voice")
async def voice_ws(websocket: WebSocket) -> None:
    container: Container = websocket.app.state.container
    token = websocket.query_params.get("token", "")

    await websocket.accept()

    # Authenticate before doing any work.
    async for session in container.db.session():
        auth = AuthService(SqlUserRepository(session), container.settings)
        try:
            user = await auth.user_from_access_token(token)
        except NovaError:
            await websocket.send_text(json.dumps({"type": "error", "detail": "unauthorized"}))
            await websocket.close(code=4401)
            return
        break

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "detail": "invalid json"}))
                continue

            kind = msg.get("type")
            conversation_id = msg.get("conversation_id")
            if kind in {"audio", "text"} and not conversation_id:
                await websocket.send_text(
                    json.dumps({"type": "error", "detail": "conversation_id required"})
                )
                continue

            # Fresh session/services per turn (unit of work).
            async for session in container.db.session():
                memory = MemoryService(SqlMemoryRepository(session))
                convos = ConversationService(
                    SqlConversationRepository(session), container.llm, memory
                )
                voice = VoiceService(container.stt, container.tts, convos)

                if kind == "text":
                    user_text = msg.get("text", "")
                    await websocket.send_text(json.dumps({"type": "transcript", "text": user_text}))
                    chunks: list[str] = []
                    async for delta in convos.stream_reply(conversation_id, user.id, user_text):
                        chunks.append(delta)
                        await websocket.send_text(json.dumps({"type": "token", "delta": delta}))
                    reply = "".join(chunks).strip()
                    await websocket.send_text(json.dumps({"type": "reply", "text": reply}))
                    audio = await voice.synthesize(reply)
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "audio",
                                "audio_b64": base64.b64encode(audio).decode("ascii"),
                                "mime": "audio/wav",
                            }
                        )
                    )
                elif kind == "audio":
                    audio_bytes = base64.b64decode(msg.get("audio_b64", ""))
                    turn = await voice.handle_turn(conversation_id, user.id, audio_bytes)
                    await websocket.send_text(
                        json.dumps({"type": "transcript", "text": turn.transcript})
                    )
                    await websocket.send_text(
                        json.dumps({"type": "reply", "text": turn.reply_text})
                    )
                    await websocket.send_text(
                        json.dumps(
                            {"type": "audio", "audio_b64": turn.audio_b64, "mime": "audio/wav"}
                        )
                    )
                elif kind == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif kind == "start":
                    await websocket.send_text(json.dumps({"type": "ready"}))
                else:
                    await websocket.send_text(
                        json.dumps({"type": "error", "detail": f"unknown type: {kind}"})
                    )
                break
    except WebSocketDisconnect:
        log.info("voice_ws_disconnect", user_id=user.id)
    except Exception as exc:  # keep the socket resilient
        log.error("voice_ws_error", error=str(exc))
        with contextlib.suppress(Exception):
            await websocket.send_text(json.dumps({"type": "error", "detail": "internal error"}))
