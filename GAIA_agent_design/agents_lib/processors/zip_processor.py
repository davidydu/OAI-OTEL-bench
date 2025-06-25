from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile
import logging

import magic

from .processor_utils import choose_processor


class ZipProcessorAgent:
    """Extract text from files inside a ZIP archive."""

    MAX_BYTES = 20000

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._magic = magic.Magic(mime=True)

    def process(self, raw: bytes, mime_type: str) -> str:
        buf = BytesIO(raw)
        texts = []
        with ZipFile(buf) as z:
            for name in z.namelist():
                if name.endswith("/"):
                    continue
                data = z.read(name)
                mime = None
                try:
                    mime = self._magic.from_buffer(data[:2048])
                except Exception:
                    pass
                processor = choose_processor(mime or "application/octet-stream")
                try:
                    text = processor.process(data, mime or "application/octet-stream")
                except Exception as e:
                    self.logger.warning("Failed processing %s: %s", name, e)
                    snippet = data[: self.MAX_BYTES]
                    text = snippet.decode("utf-8", errors="ignore")
                texts.append(f"File: {name}\n{text}")
        return "\n".join(texts)
