from __future__ import annotations

from pydantic import BaseModel
from agents import Agent
from opentelemetry import trace

from .common import AgentRequest, AgentResponse, run_with_tracing, run_in_root


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
    root_span = trace.get_current_span()

    outline_resp = await run_with_tracing(
        "deterministic.outline", story_outline_agent, req, context=ctx
    )
    if root_span.is_recording():
        root_span.add_event(
            "deterministic.outline.response",
            {"output": outline_resp.output},
        )

    checker_resp = await run_with_tracing(
        "deterministic.checker",
        outline_checker_agent,
        AgentRequest(prompt=outline_resp.output),
        context=ctx,
    )
    if root_span.is_recording():
        root_span.add_event(
            "deterministic.checker.response",
            {"output": checker_resp.output},
        )

    try:
        checker_data = OutlineCheckerOutput.model_validate_json(checker_resp.output)
    except Exception:
        checker_data = None

    if not checker_data or not (checker_data.good_quality and checker_data.is_scifi):
        return AgentResponse(output="Outline rejected")

    return await run_with_tracing(
        "deterministic.story",
        story_agent,
        AgentRequest(prompt=outline_resp.output),
        context=ctx,
    )


async def run(req: AgentRequest) -> AgentResponse:
    return await run_in_root(
        "deterministic",
        req,
        agent_name="deterministic_chain",
        chain_fn=_chain,
    )