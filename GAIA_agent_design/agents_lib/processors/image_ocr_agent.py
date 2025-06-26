from __future__ import annotations

from io import BytesIO
from typing import Dict
import base64
import openai

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


def call_vision_api(image: Image.Image, model: str = "gpt-4o") -> str:
    """Use an OpenAI vision model to describe and transcribe the image."""
    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {
                        "type": "text",
                        "text": "Describe the image in detail and transcribe any text exactly.",
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content.strip()


class ImageOCRAgent:
    """Extract text from image bytes using OCR."""

    def __init__(self) -> None:
        self._cache: Dict[str, str] = {}

    def process(self, raw: bytes, mime_type: str) -> str:
        key = str(hash(raw))
        if key in self._cache:
            return self._cache[key]
        image = Image.open(BytesIO(raw))
        try:
            text = call_vision_api(image)
        except Exception:
            image = preprocess_image(image)
            text = call_ocr_api(image).strip()
        self._cache[key] = text
        return text
