from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Dict, Optional

@dataclass(frozen=True)
class Attachment:
    path: Path     # absolute path to the media file
    data: bytes    # raw bytes (lazy‑loaded on first access)
    mime: str      # best‑effort MIME type ("application/octet‑stream" fallback)

    # Lazy property so processors that don’t need bytes avoid the read
    @property
    def bytes(self) -> bytes:  # noqa: D401 – read‑only convenience
        return self.data

class FileRouterAgent:
    """Central dispatcher that finds media files for GAIA tasks."""

    def __init__(self, media_dir: str | Path) -> None:
        self.media_dir = Path(media_dir)
        
        # map basename → full path (first match wins)
        self._index: Dict[str, Path] = {
            p.stem: p for p in media_dir.iterdir() if p.is_file()
        }

    def _guess_mime(self, path: Path) -> str:
        mime, _ = mimetypes.guess_type(path.name)
        return mime or "application/octet-stream"

    def fetch(self, task_id: str, *, return_bytes: bool = False) -> Optional[Attachment]:
        """Return the attachment for a GAIA task.

        If *return_bytes* is True we mimic the old API and return a tuple
        ``(bytes, mime)`` for legacy code.
        """
        path = self._index.get(task_id) or next((p for k, p in self._index.items() if k.startswith(task_id)), None)
        if not path:
            return None

        mime = self._guess_mime(path)
        if return_bytes:
            return path.read_bytes(), mime                # ← legacy path

        return Attachment(path=path, data=path.read_bytes(), mime=mime)
