"""Processor package exports."""

from .text_processor import TextProcessorAgent
from .docx_processor import DocxProcessorAgent
from .excel_processor import ExcelProcessorAgent
from .pdf_processor import PDFProcessorAgent
from .image_ocr_agent import ImageOCRAgent
from .audio_stt_agent import AudioSTTAgent
from .pptx_processor import PPTXProcessorAgent
from .pdb_processor import PDBProcessorAgent
from .zip_processor import ZipProcessorAgent

from .processor_utils import PROCESSORS, choose_processor

__all__ = [
    "TextProcessorAgent",
    "DocxProcessorAgent",
    "ExcelProcessorAgent",
    "PDFProcessorAgent",
    "ImageOCRAgent",
    "AudioSTTAgent",
    "PPTXProcessorAgent",
    "PDBProcessorAgent",
    "ZipProcessorAgent",
    "PROCESSORS",
    "choose_processor",
]