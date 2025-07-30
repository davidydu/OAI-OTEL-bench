from browser_use.llm import ChatOpenAI
from browser_use import Agent, BrowserProfile, BrowserSession
from dotenv import load_dotenv
load_dotenv()

from lmnr import Laminar, Instruments
import asyncio, logfire

# logfire.configure()
# logfire.instrument_httpx()
# logfire.instrument_openai_agents()

Laminar.initialize(project_api_key="qNyn09TtAUYVACdhMSZ3mZEFQeb3BYPCvGEdOe2pNFdxmQrzuDzjaQ98vEbCcuh8")

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-VL-32B-Instruct",
    base_url="https://0hu9bptnhz0xva-8000.proxy.runpod.net/v1",
    temperature = 1.0,
)


async def main():
    agent = Agent(
        task="How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.",
        llm=llm,
    )
    result = await agent.run()
    print(result.final_result())

if __name__ == "__main__":
    asyncio.run(main())