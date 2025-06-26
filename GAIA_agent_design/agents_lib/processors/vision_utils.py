from __future__ import annotations

import base64
from io import BytesIO
from typing import Any

import openai

VISION_MODEL = "gpt-4o"

def process_image_bytes(raw: bytes, prompt: str) -> str:
    """Send an image to the OpenAI vision model and return the text reply."""
    b64 = base64.b64encode(raw).decode("ascii")
    result = openai.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    return result.choices[0].message.content.strip()

def process_pdf_bytes(raw: bytes, prompt: str) -> str:
    """Send a PDF to the OpenAI vision model via file upload."""
    file_obj = BytesIO(raw)
    file = openai.files.create(file=("document.pdf", file_obj), purpose="vision")
    try:
        result = openai.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            file_ids=[file.id],
        )
    finally:
        openai.files.delete(file.id)
    return result.choices[0].message.content.strip()
