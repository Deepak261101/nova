"""Mock text-to-speech provider.

Produces a tiny valid silent WAV buffer so the frontend can treat the response as
audio without a real TTS key. The spoken text is also surfaced separately over the
websocket so the UI can display captions.
"""

from __future__ import annotations

import io
import struct
import wave

from app.domain.ports.providers import TTSProvider


def _silent_wav(duration_s: float = 0.2, sample_rate: int = 16000) -> bytes:
    n_frames = int(duration_s * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(struct.pack("<" + "h" * n_frames, *([0] * n_frames)))
    return buf.getvalue()


class MockTTSProvider(TTSProvider):
    async def synthesize(self, text: str, *, voice: str = "nova") -> bytes:
        # Duration loosely scales with text length; capped for test speed.
        duration = min(2.0, 0.05 * max(1, len(text.split())))
        return _silent_wav(duration_s=duration)
