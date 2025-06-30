from __future__ import annotations

from hashlib import sha1
from typing import Dict

from ..file_router import Attachment

from .vision_utils import process_image_bytes

DEFAULT_PROMPT = "Extract any text from this image and describe all contents in detail."


class ImageVisionAgent:
    """Use GPT-4o vision to analyze images."""

    def __init__(self, prompt: str = DEFAULT_PROMPT) -> None:
        self.prompt = prompt
        self._cache: Dict[str, str] = {}

    def process(self, att: Attachment) -> str:
        key = sha1(att.bytes).hexdigest()
        if key in self._cache:
            return self._cache[key]
        text = process_image_bytes(att.bytes, self.prompt)
        self._cache[key] = text
        return text
