from __future__ import annotations

from typing import List

from ..file_router import Attachment

import pdfplumber
from pdf2image import convert_from_bytes

from .image_ocr_agent import call_ocr_api, call_vision_api, preprocess_image


class PDFProcessorAgent:
    """Extract text from PDF documents."""

    def process(self, att: Attachment) -> str:
        """Extract text from a PDF file."""
        text_parts: List[str] = []
        if att.path.exists():
            pdf = pdfplumber.open(att.path)
        else:
            from io import BytesIO

            pdf = pdfplumber.open(BytesIO(att.bytes))
        with pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                text_parts.append(text)

        if not any(text_parts):
            images = convert_from_bytes(att.bytes)
            for img in images:
                try:
                    text_parts.append(call_vision_api(img))
                except Exception:
                    img = preprocess_image(img)
                    text_parts.append(call_ocr_api(img))

        return "\n".join(text_parts)
