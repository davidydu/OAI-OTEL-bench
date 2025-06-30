from __future__ import annotations

from hashlib import sha1
from typing import Dict

from .vision_utils import process_pdf_bytes

DEFAULT_PROMPT = "Extract any text from this image and describe all contents in detail."


class PDFVisionAgent:
    """Use GPT-4o vision to read PDFs."""

    def __init__(self, prompt: str = DEFAULT_PROMPT) -> None:
        self.prompt = prompt
        self._cache: Dict[str, str] = {}

    def process(self, raw: bytes, mime_type: str) -> str:
        key = sha1(raw).hexdigest()
        if key in self._cache:
            return self._cache[key]
        text = process_pdf_bytes(raw, self.prompt)
        self._cache[key] = text
        return text
