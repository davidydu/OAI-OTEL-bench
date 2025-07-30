import asyncio,logfire
from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent
from browser_use.llm import ChatOpenAI
from lmnr import Laminar, Instruments

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()

Laminar.initialize(project_api_key="qNyn09TtAUYVACdhMSZ3mZEFQeb3BYPCvGEdOe2pNFdxmQrzuDzjaQ98vEbCcuh8")

async def main():
    agent = Agent(
        task="A paper about AI regulation that was originally submitted to arXiv.org in June 2022 shows a figure with three axes, where each axis has a label word at both ends. Which of these words is used to describe a type of society in a Physics and Society article submitted to arXiv.org on August 11, 2016?",
        llm=ChatOpenAI(model="o4-mini", temperature=1.0),
    )
    await agent.run()

asyncio.run(main())