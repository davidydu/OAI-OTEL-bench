import asyncio
import sys
from pathlib import Path

import logfire

from .manager import GAIAResearchManager

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()


async def main(jsonl_path: str, out_path: str) -> None:
    media_dir = Path("GAIA_agent_design/gaia_media").resolve()
    manager = GAIAResearchManager(media_dir)
    await manager.run(jsonl_path, out_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ./GAIA_agent_design/run_gaia_manager.py ./GAIA/2023/validation/metadata.jsonl my_submission.jsonl ")
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
