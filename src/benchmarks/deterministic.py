from __future__ import annotations

from pydantic import BaseModel
from agents import Agent
from .common import (
    AgentRequest,
    AgentResponse,
    run_in_root,
    run_step,
)


class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_scifi: bool


story_outline_agent = Agent(
    name="story_outline_agent",
    model="gpt-4o",
    instructions="Generate a very short story outline based on the user's input.",
)

outline_checker_agent = Agent(
    name="outline_checker_agent",
    model="gpt-4o",
    instructions=(
        "Read the given story outline, judge the quality, and determine if it is a scifi story."
    ),
    output_type=OutlineCheckerOutput,
)

story_agent = Agent(
    name="story_agent",
    model="gpt-4o",
    instructions="Write a short story based on the given outline.",
    output_type=str,
)


async def _chain(req: AgentRequest, ctx) -> AgentResponse:

    outline_resp = await run_step(
        "deterministic.outline", story_outline_agent, req, ctx
    )

    checker_resp = await run_step(
        "deterministic.checker",
        outline_checker_agent,
        AgentRequest(prompt=outline_resp.output),
        ctx,
    )

    try:
        checker_data = OutlineCheckerOutput.model_validate_json(checker_resp.output)
    except Exception:
        checker_data = None

    if not checker_data or not (checker_data.good_quality and checker_data.is_scifi):
        return AgentResponse(output="Outline rejected")

    return await run_step(
        "deterministic.story",
        story_agent,
        AgentRequest(prompt=outline_resp.output),
        ctx,
    )


async def run(req: AgentRequest) -> AgentResponse:
    return await run_in_root(
        "deterministic",
        req,
        agent_name="deterministic_chain",
        chain_fn=_chain,
    )