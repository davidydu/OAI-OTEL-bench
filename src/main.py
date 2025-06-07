"""Run basic Agents SDK examples with Logfire instrumentation."""

import asyncio

import logfire
from agents import Agent, Runner, function_tool

from telemetry import tracer


FACTS = {
    "eiffel tower": "The Eiffel Tower is in Paris and was built in 1889.",
    "openai": "OpenAI is an AI research and deployment company.",
}


@function_tool
def lookup_fact(topic: str) -> str:
    """Return a short fact about the topic if known."""

    return FACTS.get(topic.lower(), "No information available.")


async def run_echo() -> None:
    """Run a simple echo agent and print the final output."""

    agent = Agent(
        name="echo_agent",
        instructions="You are a helpful assistant that echoes back what the user says.",
    )

    with tracer.start_as_current_span("use_case.echo"):
        result = await Runner.run(agent, input="Hello, OTEL!")

    print(result.final_output)


async def run_chain_of_thought() -> None:
    """Run a chain-of-thought style agent."""

    agent = Agent(
        name="cot_agent",
        instructions=(
            "You are a reasoning assistant. Think step by step before answering."
        ),
    )

    with tracer.start_as_current_span("use_case.cot"):
        result = await Runner.run(agent, input="If I have 2 apples and add 3, how many do I have?")

    print(result.final_output)


async def run_rag() -> None:
    """Run a retrieval-augmented agent using a simple lookup tool."""

    agent = Agent(
        name="rag_agent",
        instructions="Use the lookup_fact tool to answer factual questions.",
        tools=[lookup_fact],
    )

    with tracer.start_as_current_span("use_case.rag"):
        result = await Runner.run(agent, input="Tell me about the Eiffel Tower.")

    print(result.final_output)


async def main() -> None:
    """Run all basic use cases with Logfire tracing."""

    logfire.instrument_openai_agents()

    await run_echo()
    await run_chain_of_thought()
    await run_rag()


if __name__ == "__main__":
    asyncio.run(main())
