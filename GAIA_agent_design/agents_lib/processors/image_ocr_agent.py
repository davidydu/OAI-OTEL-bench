from __future__ import annotations

from io import BytesIO
from typing import Dict

import pytesseract
from PIL import Image, ImageOps


def preprocess_image(image: Image.Image) -> Image.Image:
    """Basic preprocessing to improve OCR accuracy."""
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    return image


def call_ocr_api(image: Image.Image) -> str:
    """Placeholder for external OCR service or local pytesseract."""
    return pytesseract.image_to_string(image)


class ImageOCRAgent:
    """Extract text from image bytes using OCR."""

    def __init__(self) -> None:
        self._cache: Dict[str, str] = {}

    def process(self, raw: bytes, mime_type: str) -> str:
        key = str(hash(raw))
        if key in self._cache:
            return self._cache[key]
        image = Image.open(BytesIO(raw))
        image = preprocess_image(image)
        text = call_ocr_api(image).strip()
        self._cache[key] = text
        return text
