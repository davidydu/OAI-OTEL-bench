from __future__ import annotations

from io import BytesIO
from hashlib import sha1
from typing import Dict

import openai
from pydub import AudioSegment


def call_stt_api(audio: BytesIO, model: str = "whisper-1") -> str:
    """Placeholder STT using OpenAI Whisper."""
    audio.seek(0)
    return openai.Audio.transcribe(model, audio)["text"]


class AudioSTTAgent:
    """Convert audio to text using Whisper."""

    def __init__(self, model: str = "whisper-1") -> None:
        self.model = model
        self._cache: Dict[str, str] = {}

    def process(self, raw: bytes, mime_type: str) -> str:
        key = sha1(raw).hexdigest()
        if key in self._cache:
            return self._cache[key]
        audio = AudioSegment.from_file(BytesIO(raw))
        texts = []
        # split into ~30 second chunks for whisper limits
        chunk_ms = 30 * 1000
        for i in range(0, len(audio), chunk_ms):
            chunk = audio[i : i + chunk_ms]
            buf = BytesIO()
            chunk.export(buf, format="wav")
            texts.append(call_stt_api(buf, model=self.model))
        result = " ".join(texts)
        self._cache[key] = result
        return result
