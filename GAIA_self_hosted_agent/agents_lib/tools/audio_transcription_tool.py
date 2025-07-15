from __future__ import annotations

from pathlib import Path
import mimetypes
from typing import Optional

from agents import function_tool

from ..file_router import Attachment
from ..processors.audio_stt_agent import AudioSTTAgent

_transcriber = AudioSTTAgent()

@function_tool
async def transcribe_audio(file_path: str) -> str:
    """Transcribe the given audio file to text."""
    path = Path(file_path)
    mime = mimetypes.guess_type(path.name)[0] or "audio/wav"
    att = Attachment(path=path, mime=mime)
    return await _transcriber.async_process(att)
