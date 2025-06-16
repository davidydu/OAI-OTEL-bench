import os
import asyncio

import logfire

from config import load_config
from benchmarks.runner import BenchmarkRunner
import telemetry




async def main() -> None:
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_openai_agents()
    logfire.instrument_pydantic_ai()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY in environment.")

    global tracer
    tracer = telemetry.tracer

    config = load_config()
    runner = BenchmarkRunner(config.benchmarks)
    await runner.run_all()




if __name__ == "__main__":
    asyncio.run(main())
