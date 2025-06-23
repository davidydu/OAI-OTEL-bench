# To run: python ./GAIA_agent_design/run_gaia.py ./GAIA/2023/validation/metadata.jsonl my_submission.jsonl
from __future__ import annotations

import json
from pathlib import Path

import logfire
from agents import trace
from agents.mcp import MCPServerStdio

from agents_lib.coordinator import CoordinatorAgent


logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()


async def main(jsonl_path: str, out_path: str) -> None:
    media_dir = Path("GAIA_agent_design/gaia_media").resolve()
    async with MCPServerStdio(
        name="GAIA Filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(media_dir)],
        },
    ):
        coordinator = CoordinatorAgent(media_dir)

        with open(jsonl_path) as src, open(out_path, "w") as dst:
            for line in src:
                task = json.loads(line)
                span = f"GAIA Question {task['task_id']}"
                with trace(span):
                    result = await coordinator.run_task(task)

                out = {
                    "task_id": result.task_id,
                    "model_answer": result.model_answer,
                    "reasoning_trace": result.reasoning_trace,
                    "verified": result.verified,
                }
                dst.write(json.dumps(out, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    import asyncio
    import sys

    if len(sys.argv) != 3:
        print("Usage: python run_gaia.py metadata.jsonl submission.jsonl")
        raise SystemExit(1)

    asyncio.run(main(sys.argv[1], sys.argv[2]))
