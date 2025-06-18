# /// script
# dependencies = ["logfire", "pydantic_ai_slim[openai]"]
# ///

import asyncio
import os
import logfire
from pydantic_ai import Agent


async def main():
    # Configure Logfire with token from environment
    logfire.configure(token=os.environ.get("LOGFIRE_TOKEN"))
    logfire.instrument_pydantic_ai()

    # Ensure OpenAI key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY")

    agent = Agent("openai:gpt-4o")
    result = await agent.run(
        "How does pyodide let you run Python in the browser? (short answer please)"
    )
    print(f"output: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
