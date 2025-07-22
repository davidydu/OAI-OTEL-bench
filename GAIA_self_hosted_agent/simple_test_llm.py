import logfire, asyncio
from openai import OpenAI, AsyncOpenAI
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
)

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()




client = AsyncOpenAI(api_key="x", base_url="https://0hu9bptnhz0xva-8000.proxy.runpod.net/v1")
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")

async def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model="Qwen3-8B",
    )

    result = await Runner.run(agent, "Where is Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())



