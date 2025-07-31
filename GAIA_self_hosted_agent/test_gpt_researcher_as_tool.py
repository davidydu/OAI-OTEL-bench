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
from gpt_researcher import GPTResearcher


logfire.configure(scrubbing=False)
logfire.instrument_httpx()
logfire.instrument_openai_agents()




client = AsyncOpenAI(api_key="x", base_url="https://0hu9bptnhz0xva-8000.proxy.runpod.net/v1")
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")


TOOLS = []

@function_tool
async def run_gpt_research(query: str, source: str = "web") -> str:
    """Use GPTResearcher for deeper research on a topic."""
    researcher = GPTResearcher(query=query, report_source=source)
    await researcher.conduct_research()
    return await researcher.write_report()

TOOLS.append(run_gpt_research)




async def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model="Qwen3-30B-A3B-Thinking-2507",
    )

    research_agent = Agent(
        name="SearchAgent",
        instructions="Respond with a report",
        tools=TOOLS,
        model_settings=ModelSettings(tool_choice="required"),
        model="openai/Qwen/Qwen3-30B-A3B-Thinking-2507",
    )

    result = await Runner.run(research_agent, "How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
