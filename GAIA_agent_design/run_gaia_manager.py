from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import logfire

# allow running this script either as a module or directly
if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from GAIA_agent_design.research_bot.manager import GAIAResearchManager

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()


async def main(jsonl_path: str, out_base: str, runs: int, max_concurrency: int) -> None:
    """
    Run the GAIAResearchManager `runs` times, writing each submission to
    out_base_1.jsonl, out_base_2.jsonl, ..., out_base_N.jsonl
    """
    media_dir = Path("GAIA_agent_design/gaia_media").resolve()
    manager = GAIAResearchManager(media_dir, max_concurrency=max_concurrency)

    # strip any extension from the base, to avoid double ".jsonl.jsonl"
    base = Path(out_base)
    stem = base.with_suffix("").name
    parent = base.parent

    tasks = []
    for i in range(1, runs + 1):
        out_path = parent / f"{stem}_{i}.jsonl"
        print(f"[Run {i}/{runs}] Writing to {out_path}")
        tasks.append(asyncio.create_task(manager.run(jsonl_path, str(out_path))))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print(
            "Usage: python run_gaia_manager.py <metadata.jsonl> <submission_base.jsonl> <num_runs> [max_concurrency]"
        )
        print(
            "Example: python run_gaia_manager.py metadata.jsonl my_submission.jsonl 5 20"
        )
        raise SystemExit(1)
    _, metadata, submission_base, runs_str, *extra = sys.argv
    try:
        runs = int(runs_str)
    except ValueError:
        print(f"Invalid run count: {runs_str}")
        raise SystemExit(1)

    if extra:
        try:
            concurrency = int(extra[0])
        except ValueError:
            print(f"Invalid concurrency: {extra[0]}")
            raise SystemExit(1)
    else:
        concurrency = 20

    asyncio.run(main(metadata, submission_base, runs, concurrency))
