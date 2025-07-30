import logfire, asyncio
from openai import OpenAI, AsyncOpenAI
from agents.model_settings import ModelSettings
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)
from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent as BrowserUseAgent
from browser_use.llm import ChatOpenAI
import sglang_client


logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()

client = AsyncOpenAI(api_key="x", base_url="https://0hu9bptnhz0xva-8000.proxy.runpod.net/v1")
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")


TOOLS = []
@function_tool
async def run_browser_research(query: str) -> str:
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-VL-32B-Instruct",
        base_url=sglang_client.SGLANG_BASE_URL,
    )
    browser_use_agent = BrowserUseAgent(
        task = query,
        llm = llm,
        # use_vision = False,
    )
    result = await browser_use_agent.run()
    return result.final_result() or ""

TOOLS.append(run_browser_research)


async def main():
    research_agent = Agent(
        name="SearchAgent",
        instructions="Feed the original question as the search tool query word for word. Respond with an answer.",
        tools=TOOLS,
        model_settings=ModelSettings(tool_choice="required"),
        model=sglang_client.SGLANG_MODEL,
    )

    result = await Runner.run(research_agent, "How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())