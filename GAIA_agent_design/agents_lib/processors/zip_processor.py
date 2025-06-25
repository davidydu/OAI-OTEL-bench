from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile


class ZipProcessorAgent:
    """Extract text from files inside a ZIP archive."""

    MAX_BYTES = 20000

    def process(self, raw: bytes, mime_type: str) -> str:
        buf = BytesIO(raw)
        texts = []
        with ZipFile(buf) as z:
            for name in z.namelist():
                if name.endswith("/"):
                    continue
                data = z.read(name)
                snippet = data[: self.MAX_BYTES]
                try:
                    text = snippet.decode("utf-8", errors="ignore")
                except Exception:
                    text = ""
                texts.append(f"File: {name}\n{text}")
        return "\n".join(texts)
