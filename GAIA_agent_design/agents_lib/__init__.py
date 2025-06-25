from .file_router import FileRouterAgent

from .processors import (
    PROCESSORS,
    choose_processor,
    TextProcessorAgent,
    DocxProcessorAgent,
    ExcelProcessorAgent,
    PDFProcessorAgent,
    ImageOCRAgent,
    AudioSTTAgent,
)

__all__ = [
    "FileRouterAgent",
    "TextProcessorAgent",
    "DocxProcessorAgent",
    "ExcelProcessorAgent",
    "PDFProcessorAgent",
    "ImageOCRAgent",
    "AudioSTTAgent",
    "PROCESSORS",
    "choose_processor",
]
