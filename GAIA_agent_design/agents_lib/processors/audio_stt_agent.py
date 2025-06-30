from __future__ import annotations

from openai import OpenAI


from ..file_router import Attachment

__all__ = ["AudioSTTAgent"]


class AudioSTTAgent:
    """Transcribe audio files to text using the OpenAI Agents voice stack."""

    def __init__(self, model: str = "gpt-4o-transcribe") -> None:
        self.model = model

    def process(self, att: Attachment):
        client = OpenAI()
        if att.path.exists():
            audio_file = open(att.path, "rb")
        transcription = client.audio.transcriptions.create(
            model=self.model, 
            file=audio_file, 
            response_format="text",
        )
        return transcription