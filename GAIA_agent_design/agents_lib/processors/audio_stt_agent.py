from __future__ import annotations

from hashlib import sha1
from typing import Dict

import openai

from ..file_router import Attachment

__all__ = ["AudioSTTAgent"]


class AudioSTTAgent:
    def __init__(self, model: str = "gpt-4o-audio-preview-2025-06-03") -> None:
        self.model = model
        self._cache: Dict[str, str] = {}

    def process(self, att: Attachment) -> str:
        key = sha1(att.bytes).hexdigest()
        if key in self._cache:
            return self._cache[key]

        if att.path.exists():
            with att.path.open("rb") as f:
                resp = openai.Audio.transcribe(self.model, f)
        else:
            from io import BytesIO

            resp = openai.Audio.transcribe(self.model, BytesIO(att.bytes))
        text = resp["text"].strip()
        self._cache[key] = text
        return text
