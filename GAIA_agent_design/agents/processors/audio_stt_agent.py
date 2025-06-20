from __future__ import annotations

from io import BytesIO

import openai


def call_stt_api(audio: BytesIO, model: str = "whisper-1") -> str:
    """Placeholder STT using OpenAI Whisper."""
    audio.seek(0)
    return openai.Audio.transcribe(model, audio)["text"]


class AudioSTTAgent:
    """Convert audio to text using Whisper."""

    def __init__(self, model: str = "whisper-1") -> None:
        self.model = model

    def process(self, raw: bytes, mime_type: str) -> str:
        return call_stt_api(BytesIO(raw), model=self.model)
