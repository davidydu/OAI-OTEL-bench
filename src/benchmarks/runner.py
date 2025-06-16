from __future__ import annotations

import importlib
from typing import Sequence

from ..config import BenchmarkItem
from .common import AgentRequest


class BenchmarkRunner:
    def __init__(self, benchmarks: Sequence[BenchmarkItem]):
        self.benchmarks = benchmarks

    async def run_all(self) -> None:
        for bench in self.benchmarks:
            module = importlib.import_module(f"src.benchmarks.{bench.name}")
            run_func = getattr(module, "run")
            resp = await run_func(AgentRequest(prompt=bench.prompt))
            print(resp.output)
