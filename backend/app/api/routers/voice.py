"""Voice REST endpoints (TTS synth + STT transcription helpers).

The primary real-time path is the ``/ws/voice`` websocket; these REST endpoints
are convenient for testing and non-streaming clients.
"""

from __future__ import annotations

import base64

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from app.api.deps import CurrentUser, VoiceServiceDep

router = APIRouter(prefix="/voice", tags=["voice"])


class SynthRequest(BaseModel):
    text: str
    voice: str = "nova"


class SynthResponse(BaseModel):
    audio_b64: str
    mime: str = "audio/wav"


class TranscribeResponse(BaseModel):
    transcript: str


@router.post("/synthesize", response_model=SynthResponse)
async def synthesize(
    body: SynthRequest, user: CurrentUser, voice: VoiceServiceDep
) -> SynthResponse:
    audio = await voice.synthesize(body.text, voice=body.voice)
    return SynthResponse(audio_b64=base64.b64encode(audio).decode("ascii"))


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile, user: CurrentUser, voice: VoiceServiceDep
) -> TranscribeResponse:
    audio = await file.read()
    transcript = await voice.transcribe(audio)
    return TranscribeResponse(transcript=transcript)
