from agents import Agent, function_tool

from .common import AgentRequest, AgentResponse, run_with_tracing


FACTS = {
    "eiffel tower": "The Eiffel Tower is in Paris and was built in 1889.",
    "openai": "OpenAI is an AI research and deployment company.",
}


@function_tool
def lookup_fact(topic: str) -> str:
    return FACTS.get(topic.lower(), "No information available.")


async def run(req: AgentRequest) -> AgentResponse:
    agent = Agent(
        name="rag_agent",
        model="gpt-4o",
        instructions="Use the lookup_fact tool to answer factual questions.",
        tools=[lookup_fact],
    )
    return await run_with_tracing("rag", agent, req)
