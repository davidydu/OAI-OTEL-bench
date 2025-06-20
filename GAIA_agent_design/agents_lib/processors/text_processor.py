from __future__ import annotations

import json
from typing import Tuple


class TextProcessorAgent:
    """Process plain text, JSON, or Python source files."""

    def process(self, raw: bytes, mime_type: str) -> str:
        """Return decoded text for text-like mime types."""
        if mime_type.startswith("text/") or "json" in mime_type or "python" in mime_type:
            text = raw.decode("utf-8", errors="ignore")
            # pretty print JSON if possible
            try:
                obj = json.loads(text)
                return json.dumps(obj, indent=2, ensure_ascii=False)
            except Exception:
                return text
        # If not recognized as text, just decode best effort
        return raw.decode("utf-8", errors="ignore")
