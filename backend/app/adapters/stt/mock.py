"""Mock speech-to-text provider.

Returns a placeholder transcript so the voice pipeline works without an STT key.
If the incoming audio buffer carries UTF-8 text (as the mock frontend/test client
sends), it is decoded and returned verbatim to make end-to-end tests meaningful.
"""

from __future__ import annotations

from app.domain.ports.providers import STTProvider


class MockSTTProvider(STTProvider):
    async def transcribe(self, audio: bytes, *, sample_rate: int = 16000) -> str:
        try:
            text = audio.decode("utf-8").strip()
        except UnicodeDecodeError:
            text = ""
        return text or "[unrecognized audio]"
