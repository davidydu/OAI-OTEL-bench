from browser_use.llm import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()

import asyncio, logfire

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()

llm = ChatOpenAI(
    model="Qwen/Qwen3-30B-A3B",
    base_url="https://0hu9bptnhz0xva-8000.proxy.runpod.net/v1",
    temperature = 0.0,
)


async def main():
    agent = Agent(
        task="How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.",
        llm=llm,
        use_vision=False,
    )
    result = await agent.run()
    print(result.final_result())

if __name__ == "__main__":
    asyncio.run(main())