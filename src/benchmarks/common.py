from __future__ import annotations

from opentelemetry import trace
from pydantic import BaseModel
from agents import Runner



class AgentRequest(BaseModel):
    prompt: str


class AgentResponse(BaseModel):
    output: str


async def run_with_tracing(
    use_case: str,
    agent,
    req: AgentRequest,
    *,
    context=None,
) -> AgentResponse:

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(
        f"use_case.{use_case}", context=context
    ) as span:
        agent_name = getattr(agent, "name", None)
        if isinstance(agent_name, str):
            span.set_attribute("agent.name", agent_name)

        resolved_model = getattr(agent, "model_name", None) or getattr(
            agent, "model", None
        )
        if resolved_model is not None:
            model_str = (
                resolved_model
                if isinstance(resolved_model, str)
                else str(resolved_model)
            )
            span.set_attribute("model.name", model_str)

        instructions = getattr(agent, "instructions", None)
        if isinstance(instructions, str):
            span.set_attribute("agent.instructions", instructions)

        tools = getattr(agent, "tools", None)
        if isinstance(tools, (list, tuple)) and tools:
            tool_names = []
            for t in tools:
                fn = getattr(t, "__wrapped__", t)
                name = getattr(fn, "__name__", None)
                if name:
                    tool_names.append(name)
            if tool_names:
                span.set_attribute("agent.tools", tool_names)

        span.add_event("agent.request", req.model_dump())

        if hasattr(agent, "run") and callable(agent.run):
            result = await agent.run(req.prompt)
        else:
            result = await Runner.run(agent, input=req.prompt)

        resp_value = getattr(result, "final_output", None) or getattr(
            result, "output", None
        )
        if not isinstance(resp_value, str):
            if hasattr(resp_value, "model_dump_json"):
                resp_value = resp_value.model_dump_json()
            else:
                resp_value = str(resp_value)

        resp = AgentResponse(output=resp_value)
        span.add_event("agent.response", resp.model_dump())
        return resp

async def run_step(
    use_case: str,
    agent,
    req: AgentRequest,
    ctx,
) -> AgentResponse:
    """Execute an agent call and log the output on the parent span."""

    resp = await run_with_tracing(use_case, agent, req, context=ctx)
    parent = trace.get_current_span()
    if parent.is_recording():
        parent.add_event(f"{use_case}.response", {"output": resp.output})
    return resp

async def run_in_root(
    use_case: str,
    req: AgentRequest,
    agent_name: str | None,
    chain_fn,
) -> AgentResponse:
    """Run a sequence of agent calls under a root span."""

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(f"use_case.{use_case}") as span:
        if agent_name:
            span.set_attribute("agent.name", agent_name)
        span.add_event("agent.request", req.model_dump())

        ctx = trace.set_span_in_context(span)
        resp = await chain_fn(req, ctx)

        span.add_event("agent.response", resp.model_dump())
        return resp