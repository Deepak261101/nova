"""Voice-loop use-case: STT -> conversation -> TTS.

Wake-word detection ("Hey Nova") is performed client-side to gate the mic; the
backend receives already-triggered audio turns.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass

from app.domain.ports.providers import STTProvider, TTSProvider
from app.services.conversation import ConversationService


@dataclass(slots=True)
class VoiceTurn:
    transcript: str
    reply_text: str
    audio_b64: str


class VoiceService:
    def __init__(
        self,
        stt: STTProvider,
        tts: TTSProvider,
        conversations: ConversationService,
    ) -> None:
        self._stt = stt
        self._tts = tts
        self._conversations = conversations

    async def transcribe(self, audio: bytes, *, sample_rate: int = 16000) -> str:
        return await self._stt.transcribe(audio, sample_rate=sample_rate)

    async def synthesize(self, text: str, *, voice: str = "nova") -> bytes:
        return await self._tts.synthesize(text, voice=voice)

    async def handle_turn(
        self, conversation_id: str, user_id: str, audio: bytes, *, voice: str = "nova"
    ) -> VoiceTurn:
        transcript = await self.transcribe(audio)
        message = await self._conversations.reply(conversation_id, user_id, transcript)
        audio_out = await self.synthesize(message.content, voice=voice)
        return VoiceTurn(
            transcript=transcript,
            reply_text=message.content,
            audio_b64=base64.b64encode(audio_out).decode("ascii"),
        )
