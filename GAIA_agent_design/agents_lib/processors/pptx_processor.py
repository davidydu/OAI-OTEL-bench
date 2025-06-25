from __future__ import annotations

from io import BytesIO
from pptx import Presentation


class PPTXProcessorAgent:
    """Extract text from PowerPoint presentations."""

    def process(self, raw: bytes, mime_type: str) -> str:
        pres = Presentation(BytesIO(raw))
        texts = []
        for slide in pres.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    txt = shape.text.strip()
                    if txt:
                        texts.append(txt)
        return "\n".join(texts)
