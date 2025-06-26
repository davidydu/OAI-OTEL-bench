from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile
import logging
import mimetypes

try:
    import magic
except Exception:  # pragma: no cover - optional dependency may be missing
    magic = None

from .processor_utils import choose_processor


class ZipProcessorAgent:
    """Extract text from files inside a ZIP archive."""

    MAX_BYTES = 20000

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        if magic:
            try:
                self._magic = magic.Magic(mime=True)
            except Exception:
                self._magic = None
        else:
            self._magic = None

    def process(self, raw: bytes, mime_type: str) -> str:
        buf = BytesIO(raw)
        texts = []
        with ZipFile(buf) as z:
            for name in z.namelist():
                if name.endswith("/"):
                    continue
                data = z.read(name)
                mime = None
                if self._magic is not None:
                    try:
                        mime = self._magic.from_buffer(data[:2048])
                    except Exception:
                        pass
                if not mime:
                    mime, _ = mimetypes.guess_type(name)
                processor = choose_processor(mime or "application/octet-stream")
                try:
                    text = processor.process(data, mime or "application/octet-stream")
                except Exception as e:
                    self.logger.warning("Failed processing %s: %s", name, e)
                    snippet = data[: self.MAX_BYTES]
                    text = snippet.decode("utf-8", errors="ignore")
                texts.append(f"File: {name}\n{text}")
        return "\n".join(texts)
