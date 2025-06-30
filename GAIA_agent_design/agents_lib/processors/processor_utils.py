from __future__ import annotations
from typing import Dict, Protocol
from ..file_router import Attachment


class FileProcessor(Protocol):
    """Protocol for processor classes."""

    def process(self, att: Attachment) -> str: ...


"""Utilities for choosing the right processor for a given MIME type."""

from .text_processor import TextProcessorAgent
from .docx_processor import DocxProcessorAgent
from .excel_processor import ExcelProcessorAgent
from .pdf_vision_agent import PDFVisionAgent
from .image_vision_agent import ImageVisionAgent
from .audio_stt_agent import AudioSTTAgent
from .pptx_processor import PPTXProcessorAgent
from .pdb_processor import PDBProcessorAgent
from .zip_processor import ZipProcessorAgent

PROCESSORS = {
    "text": TextProcessorAgent(),
    "docx": DocxProcessorAgent(),
    "excel": ExcelProcessorAgent(),
    "pdf": PDFVisionAgent(),
    "image": ImageVisionAgent(),
    "audio": AudioSTTAgent(),
    "pptx": PPTXProcessorAgent(),
    "pdb": PDBProcessorAgent(),
    "zip": ZipProcessorAgent(),
}


def choose_processor(mime: str):
    if mime.startswith("text/") or "json" in mime or "python" in mime:
        return PROCESSORS["text"]
    if "word" in mime:
        return PROCESSORS["docx"]
    if "excel" in mime or "spreadsheet" in mime:
        return PROCESSORS["excel"]
    if "pdf" in mime:
        return PROCESSORS["pdf"]
    if mime.startswith("image/"):
        return PROCESSORS["image"]
    if mime.startswith("audio/"):
        return PROCESSORS["audio"]
    if "zip" in mime:
        return PROCESSORS["zip"]
    if "presentation" in mime or mime.endswith("pptx"):
        return PROCESSORS["pptx"]
    if "pdb" in mime:
        return PROCESSORS["pdb"]
    return PROCESSORS["text"]
