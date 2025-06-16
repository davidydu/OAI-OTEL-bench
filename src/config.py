from __future__ import annotations

from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel


class BenchmarkItem(BaseModel):
    name: str
    prompt: str


class AppConfig(BaseModel):
    benchmarks: List[BenchmarkItem]


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    path = Path(path)
    if path.exists():
        data = yaml.safe_load(path.read_text()) or {}
    else:
        data = {}
    return AppConfig.model_validate(data)
