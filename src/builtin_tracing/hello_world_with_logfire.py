import asyncio
import os
import logfire
from pathlib import Path
import sys

"""Run the Agents SDK hello world example with Logfire tracing."""

# Ensure the submodule is on the import path
submodule_path = Path(__file__).resolve().parents[1] / "openai_agents" / "src"
sys.path.append(str(submodule_path))

from agents import Agent, Runner


async def main() -> None:
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    # Automatically convert Agents SDK traces to Logfire spans.
    logfire.instrument_openai_agents()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY")

    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
