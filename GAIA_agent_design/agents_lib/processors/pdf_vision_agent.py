from __future__ import annotations

from hashlib import sha1
from typing import Dict

from ..file_router import Attachment

from .vision_utils import process_pdf_bytes

DEFAULT_PROMPT = "Extract any text from this image and describe all contents in detail."


class PDFVisionAgent:
    """Use GPT-4o vision to read PDFs."""

    def __init__(self, prompt: str = DEFAULT_PROMPT) -> None:
        self.prompt = prompt
        self._cache: Dict[str, str] = {}

    def process(self, att: Attachment) -> str:
        key = sha1(att.bytes).hexdigest()
        if key in self._cache:
            return self._cache[key]
        text = process_pdf_bytes(att.bytes, self.prompt)
        self._cache[key] = text
        return text
