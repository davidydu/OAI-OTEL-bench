from __future__ import annotations

from io import BytesIO
from typing import Tuple

import pandas as pd


class ExcelProcessorAgent:
    """Convert Excel sheets to CSV-formatted text."""

    def process(self, raw: bytes, mime_type: str) -> str:
        file_like = BytesIO(raw)
        excel = pd.ExcelFile(file_like)
        texts = []
        for sheet in excel.sheet_names:
            df = excel.parse(sheet)
            texts.append(df.to_csv(index=False))
        return "\n".join(texts)
