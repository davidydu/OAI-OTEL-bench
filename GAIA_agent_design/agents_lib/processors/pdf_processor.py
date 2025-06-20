from __future__ import annotations

from io import BytesIO

import pdfplumber


class PDFProcessorAgent:
    """Extract text from PDF documents."""

    def process(self, raw: bytes, mime_type: str) -> str:
        file_like = BytesIO(raw)
        text_parts = []
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)
