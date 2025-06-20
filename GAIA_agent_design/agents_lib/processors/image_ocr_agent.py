from __future__ import annotations

from io import BytesIO
from typing import Tuple

import pytesseract
from PIL import Image


def call_ocr_api(image: Image.Image) -> str:
    """Placeholder for external OCR service."""
    return pytesseract.image_to_string(image)


class ImageOCRAgent:
    """Extract text from image bytes using OCR."""

    def process(self, raw: bytes, mime_type: str) -> str:
        image = Image.open(BytesIO(raw))
        text = call_ocr_api(image)
        return text.strip()
