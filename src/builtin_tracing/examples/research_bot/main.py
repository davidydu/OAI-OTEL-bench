import asyncio

from .manager import ResearchManager

import logfire
# instrumentation
logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()

async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    asyncio.run(main())
