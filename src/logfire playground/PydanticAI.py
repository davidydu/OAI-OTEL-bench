# /// script
# dependencies = ["logfire", "pydantic_ai_slim[openai]"]
# ///

# This example demonstrates PydanticAI running with OpenAI!

import asyncio, os
from pydantic_ai import Agent
import logfire

async def main():
    # configure logfire
    logfire.configure(token="pylf_v1_us_9bZ57RDYs2P0LbbxcjK95kxZKL0jqFDhKqjYtTR7Wwy7")
    logfire.instrument_pydantic_ai()

    os.environ["OPENAI_API_KEY"] = "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"

    agent = Agent("openai:gpt-4o")
    result = await agent.run(
        "How does pyodide let you run Python in the browser? (short answer please)"
    )
    print(f"output: {result.output}")

if __name__ == "__main__":
    asyncio.run(main())