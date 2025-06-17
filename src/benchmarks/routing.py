from __future__ import annotations

from agents import Agent

import uuid

from .common import (
    AgentRequest,
    AgentResponse,
    run_streamed_with_tracing,
)

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
    conversation_id = uuid.uuid4().hex[:8]
    agent = triage_agent
    inputs = [{"content": req.prompt, "role": "user"}]

    resp, agent, inputs = await run_streamed_with_tracing(
        "routing.turn1", agent, inputs, attributes={"conversation.id": conversation_id}
    )

    inputs.append({"content": "Thanks!", "role": "user"})
    resp, agent, inputs = await run_streamed_with_tracing(
        "routing.turn2", agent, inputs, attributes={"conversation.id": conversation_id}
    )

    return resp