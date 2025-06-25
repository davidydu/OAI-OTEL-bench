from __future__ import annotations

import os
import mimetypes
from pathlib import Path
from typing import Dict, Tuple

import magic


class FileRouterAgent:
    """Simple utility to fetch GAIA media files."""

    def __init__(self, media_dir: str | Path) -> None:
        self.media_dir = Path(media_dir)
        if not self.media_dir.exists():
            raise FileNotFoundError(f"Media directory {self.media_dir} not found")
        # MIME detector
        self._magic = magic.Magic(mime=True)
        # Build an index of task_id -> file path for quick lookup
        self._index: Dict[str, Path] = {}
        for fname in os.listdir(self.media_dir):
            path = self.media_dir / fname
            if path.is_file():
                key = fname.split(".")[0]
                if key not in self._index:
                    self._index[key] = path

    def fetch(self, task_id: str) -> Tuple[bytes | None, str | None]:
        """Return raw bytes and detected MIME for the file matching ``task_id``."""
        path = self._index.get(task_id)
        if path is None:
            # fall back to prefix search
            matches = [f for f in os.listdir(self.media_dir) if f.startswith(task_id)]
            if not matches:
                return None, None
            path = self.media_dir / matches[0]
        with open(path, "rb") as fh:
            data = fh.read()
        mime_type = self._magic.from_buffer(data[:2048])
        if mime_type == "application/octet-stream" or mime_type is None:
            guessed, _ = mimetypes.guess_type(path.name)
            if guessed:
                mime_type = guessed
        return data, mime_type
