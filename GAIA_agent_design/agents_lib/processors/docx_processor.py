from __future__ import annotations

from io import BytesIO
from typing import List

from docx import Document


class DocxProcessorAgent:
    """Extract text from .docx files."""

    def process(self, raw: bytes, mime_type: str) -> str:
        file_like = BytesIO(raw)
        doc = Document(file_like)
        texts: List[str] = [p.text for p in doc.paragraphs if p.text]
        for table in doc.tables:
            for row in table.rows:
                row_text = "\t".join(cell.text.strip() for cell in row.cells)
                if row_text.strip():
                    texts.append(row_text)
        return "\n".join(texts)
