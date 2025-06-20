from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

import magic


class FileRouterAgent:
    """Simple utility to fetch GAIA media files."""

    def __init__(self, media_dir: str | Path) -> None:
        self.media_dir = Path(media_dir)
        if not self.media_dir.exists():
            raise FileNotFoundError(f"Media directory {self.media_dir} not found")
        # MIME detector
        self._magic = magic.Magic(mime=True)

    def fetch(self, task_id: str) -> Tuple[bytes, str]:
        """Return raw bytes and detected MIME for the file matching ``task_id``."""
        matches = [f for f in os.listdir(self.media_dir) if f.startswith(task_id)]
        if not matches:
            raise FileNotFoundError(f"No file starting with {task_id}")
        path = self.media_dir / matches[0]
        with open(path, "rb") as fh:
            data = fh.read()
        mime_type = self._magic.from_buffer(data[:2048])
        return data, mime_type
