from __future__ import annotations

from agents import Agent

from .common import AgentRequest, AgentResponse, run_with_tracing

french_agent = Agent(
    name="french_agent",
    model="gpt-4o",
    instructions="You only speak French",
)

spanish_agent = Agent(
    name="spanish_agent",
    model="gpt-4o",
    instructions="You only speak Spanish",
)

english_agent = Agent(
    name="english_agent",
    model="gpt-4o",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="triage_agent",
    model="gpt-4o",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[french_agent, spanish_agent, english_agent],
)


async def run(req: AgentRequest) -> AgentResponse:
    return await run_with_tracing("routing", triage_agent, req)