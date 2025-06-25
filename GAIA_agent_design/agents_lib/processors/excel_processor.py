from __future__ import annotations

from io import BytesIO
from typing import List

from openpyxl import load_workbook
import csv
import io


class ExcelProcessorAgent:
    """Convert Excel sheets to CSV-formatted text."""

    def process(self, raw: bytes, mime_type: str) -> str:
        wb = load_workbook(BytesIO(raw), data_only=False)
        texts: List[str] = []
        for sheet in wb.worksheets:
            output = io.StringIO()
            writer = csv.writer(output)
            for row in sheet.iter_rows():
                vals = []
                for cell in row:
                    if cell.data_type == "f":
                        vals.append(f"FORMULA:{cell.value}")
                    else:
                        vals.append(cell.value if cell.value is not None else "")
                writer.writerow(vals)
            texts.append(f"Sheet: {sheet.title}\n{output.getvalue()}")
        return "\n".join(texts)
