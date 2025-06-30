from __future__ import annotations

from hashlib import sha1
from typing import Dict

import numpy as np
from pydub import AudioSegment
from agents.voice import AudioInput, OpenAIVoiceModelProvider, STTModelSettings

from ..file_router import Attachment

__all__ = ["AudioSTTAgent"]


class AudioSTTAgent:
    """Transcribe audio files to text using the OpenAI Agents voice stack."""

    def __init__(self, model: str = "gpt-4o-transcribe") -> None:
        self.model = model
        self._provider = OpenAIVoiceModelProvider()
        self._cache: Dict[str, str] = {}

    def _prepare_audio(self, att: Attachment) -> AudioInput:
        if att.path.exists():
            seg = AudioSegment.from_file(att.path)
        else:
            from io import BytesIO

            seg = AudioSegment.from_file(BytesIO(att.bytes))

        seg = seg.set_frame_rate(24000).set_channels(1).set_sample_width(2)
        buffer = np.array(seg.get_array_of_samples(), dtype=np.int16)
        return AudioInput(
            buffer=buffer,
            frame_rate=seg.frame_rate,
            sample_width=seg.sample_width,
            channels=seg.channels,
        )

    async def async_process(self, att: Attachment) -> str:
        key = sha1(att.bytes).hexdigest()
        if key in self._cache:
            return self._cache[key]

        audio_input = self._prepare_audio(att)
        model = self._provider.get_stt_model(self.model)
        text = await model.transcribe(
            audio_input,
            STTModelSettings(),
            trace_include_sensitive_data=False,
            trace_include_sensitive_audio_data=False,
        )
        text = text.strip()
        self._cache[key] = text
        return text

    def process(self, att: Attachment) -> str:
        """Synchronous wrapper around :meth:`async_process`."""
        import asyncio

        return asyncio.run(self.async_process(att))
