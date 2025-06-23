from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import logfire

# Allow running this script either as part of the GAIA_agent_design package
# (`python -m GAIA_agent_design.run_gaia_manager`) or directly via a file path
if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from GAIA_agent_design.research_bot.manager import GAIAResearchManager

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()


async def main(jsonl_path: str, out_path: str) -> None:
    media_dir = Path("GAIA_agent_design/gaia_media").resolve()
    manager = GAIAResearchManager(media_dir)
    await manager.run(jsonl_path, out_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_gaia_manager.py metadata.jsonl submission.jsonl")
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
