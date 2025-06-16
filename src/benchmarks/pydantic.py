from pydantic_ai import Agent as PydanticAgent

from .common import AgentRequest, AgentResponse, run_with_tracing


async def run(req: AgentRequest) -> AgentResponse:
    agent = PydanticAgent("openai:gpt-4o")
    return await run_with_tracing("pydantic", agent, req)
