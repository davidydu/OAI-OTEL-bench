from browser_use.llm import ChatOpenAI
from browser_use import Agent, BrowserProfile, BrowserSession
from dotenv import load_dotenv
load_dotenv()

import asyncio, logfire

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()

llm = ChatOpenAI(
    model="google/gemma-3-27b-it",
    base_url="https://0hu9bptnhz0xva-8000.proxy.runpod.net/v1",
    temperature = 0.0,
)


async def main():
    session = BrowserSession(browser_profile=BrowserProfile(headless=True))
    agent = Agent(
        task="How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.",
        llm=llm,
        # use_vision=False,
        browser_session=session,
        
    )
    result = await agent.run()
    print(result.final_result())

if __name__ == "__main__":
    asyncio.run(main())