from __future__ import annotations

from io import BytesIO
from typing import List

import pdfplumber
from pdf2image import convert_from_bytes

from .image_ocr_agent import call_ocr_api, preprocess_image


class PDFProcessorAgent:
    """Extract text from PDF documents."""

    def process(self, raw: bytes, mime_type: str) -> str:
        file_like = BytesIO(raw)
        text_parts: List[str] = []
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                text_parts.append(text)

        if not any(text_parts):
            images = convert_from_bytes(raw)
            for img in images:
                img = preprocess_image(img)
                text_parts.append(call_ocr_api(img))

        return "\n".join(text_parts)
