from agents import Agent

from .common import AgentRequest, AgentResponse, run_with_tracing


async def run(req: AgentRequest) -> AgentResponse:
    agent = Agent(
        name="echo_agent",
        model="gpt-4o",
        instructions="You are a helpful assistant that echoes back what the user says.",
    )
    return await run_with_tracing("echo", agent, req)
