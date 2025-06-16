from __future__ import annotations

import asyncio
from agents import Agent
from opentelemetry import trace

from .common import AgentRequest, AgentResponse, run_with_tracing, run_in_root

spanish_agent = Agent(
    name="spanish_agent",
    model="gpt-4o",
    instructions="You translate the user's message to Spanish",
)

translation_picker = Agent(
    name="translation_picker",
    model="gpt-4o",
    instructions="You pick the best Spanish translation from the given options.",
)


async def _chain(req: AgentRequest, ctx) -> AgentResponse:
    root_span = trace.get_current_span()

    res1, res2, res3 = await asyncio.gather(
        run_with_tracing("parallelization.translate", spanish_agent, req, context=ctx),
        run_with_tracing("parallelization.translate", spanish_agent, req, context=ctx),
        run_with_tracing("parallelization.translate", spanish_agent, req, context=ctx),
    )

    translations = "\n\n".join([res1.output, res2.output, res3.output])
    if root_span.is_recording():
        root_span.add_event(
            "parallelization.translations",
            {"translations": translations},
        )

    pick_req = AgentRequest(
        prompt=f"Input: {req.prompt}\n\nTranslations:\n{translations}"
    )
    return await run_with_tracing(
        "parallelization.pick",
        translation_picker,
        pick_req,
        context=ctx,
    )


async def run(req: AgentRequest) -> AgentResponse:
    return await run_in_root(
        "parallelization",
        req,
        agent_name="parallelization_chain",
        chain_fn=_chain,
    )