from __future__ import annotations

import mimetypes
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Attachment:
    """Representation of a file attachment."""

    path: Path
    mime: str
    _data: bytes | None = field(default=None, repr=False)

    @property
    def bytes(self) -> bytes:  # noqa: D401 - convenient alias
        """Return the file bytes, reading from disk on first access."""
        if self._data is None:
            self._data = self.path.read_bytes()
        return self._data


class FileRouterAgent:
    """Central dispatcher that finds media files for GAIA tasks."""

    def __init__(self, media_dir: str | Path) -> None:
        self.media_dir = Path(media_dir)

        # map basename → full path (first match wins)
        self._index: Dict[str, Path] = {
            p.stem: p for p in self.media_dir.iterdir() if p.is_file()
        }

    def _guess_mime(self, path: Path) -> str:
        mime, _ = mimetypes.guess_type(path.name)
        return mime or "application/octet-stream"

    def fetch(
        self, task_id: str, *, return_bytes: bool = False
    ) -> Optional[Attachment]:
        """Return the attachment for a GAIA task.

        If *return_bytes* is True we mimic the old API and return a tuple
        ``(bytes, mime)`` for legacy code.
        """
        path = self._index.get(task_id) or next(
            (p for k, p in self._index.items() if k.startswith(task_id)), None
        )
        if not path:
            return None

        mime = self._guess_mime(path)
        if return_bytes:
            return path.read_bytes(), mime  # ← legacy path

        return Attachment(path=path, mime=mime)
