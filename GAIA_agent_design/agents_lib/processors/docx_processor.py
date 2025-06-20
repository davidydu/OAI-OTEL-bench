from __future__ import annotations

from io import BytesIO
from typing import Tuple

from docx import Document


class DocxProcessorAgent:
    """Extract text from .docx files."""

    def process(self, raw: bytes, mime_type: str) -> str:
        file_like = BytesIO(raw)
        doc = Document(file_like)
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs)
