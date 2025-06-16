from agents import Agent

from .common import AgentRequest, AgentResponse, run_with_tracing


async def run(req: AgentRequest) -> AgentResponse:
    agent = Agent(
        name="cot_agent",
        model="o1",
        instructions="You are a reasoning assistant. Think step by step before answering.",
    )
    return await run_with_tracing("cot", agent, req)
