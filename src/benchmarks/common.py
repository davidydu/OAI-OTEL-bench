from __future__ import annotations

from typing import Any, Iterable
import json

from opentelemetry import trace
from pydantic import BaseModel
from agents import Runner, ItemHelpers, MessageOutputItem


class AgentRequest(BaseModel):
    prompt: Any


class AgentResponse(BaseModel):
    output: str


def add_event(event_name: str, attributes: dict[str, Any] | None = None) -> None:
    """Attach an event to the current span if recording."""
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(event_name, attributes or {})


async def run_with_tracing(
    use_case: str,
    agent,
    req: AgentRequest,
    *,
    context=None,
    attributes: dict[str, Any] | None = None,
    return_result: bool = False,
) -> AgentResponse:

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(f"use_case.{use_case}", context=context) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
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

        req_dict = req.model_dump()
        prompt_val = req_dict.get("prompt")
        if (
            not isinstance(prompt_val, (str, bytes, int, float, bool))
            and prompt_val is not None
        ):
            try:
                req_dict["prompt"] = json.dumps(prompt_val)
            except TypeError:
                req_dict["prompt"] = str(prompt_val)
        span.add_event("agent.request", req_dict)

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
        if return_result:
            return resp, result
        return resp


async def run_step(
    use_case: str,
    agent,
    req: AgentRequest,
    ctx,
    *,
    attributes: dict[str, Any] | None = None,
) -> AgentResponse:
    """Execute an agent call and log the output on the parent span."""

    resp = await run_with_tracing(
        use_case, agent, req, context=ctx, attributes=attributes
    )
    parent = trace.get_current_span()
    if parent.is_recording():
        parent.add_event(f"{use_case}.response", {"output": resp.output})
    return resp


async def run_streamed_with_tracing(
    use_case: str,
    agent,
    inputs: Iterable[dict[str, Any]],
    *,
    context=None,
    agent_context=None,
    attributes: dict[str, Any] | None = None,
) -> tuple[AgentResponse, Any, list[dict[str, Any]]]:
    """Run an agent with streaming and return the updated conversation."""

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span(f"use_case.{use_case}", context=context) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        # Logfire only allows primitive attribute types, so we serialize the
        # message list to JSON instead of passing nested dicts directly.
        span.add_event("agent.request", {"messages": json.dumps(list(inputs))})

        result = Runner.run_streamed(agent, input=list(inputs), context=agent_context)
        async for _ in result.stream_events():
            pass

        resp_value = result.final_output
        if not isinstance(resp_value, str):
            resp_value = str(resp_value)

        resp = AgentResponse(output=resp_value)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        req_dict = resp.model_dump()
        prompt_val = req_dict.get("prompt")
        if (
            not isinstance(prompt_val, (str, bytes, int, float, bool))
            and prompt_val is not None
        ):
            try:
                req_dict["prompt"] = json.dumps(prompt_val)
            except TypeError:
                req_dict["prompt"] = str(prompt_val)
        span.add_event("agent.request", req_dict)

        return resp, result.current_agent, result.to_input_list()


async def run_in_root(
    use_case: str,
    req: AgentRequest,
    agent_name: str | None,
    chain_fn,
    *,
    attributes: dict[str, Any] | None = None,
) -> AgentResponse:
    """Run a sequence of agent calls under a root span."""


    tracer = trace.get_tracer(__name__)


    with tracer.start_as_current_span(f"use_case.{use_case}") as span:

        if agent_name:
            span.set_attribute("agent.name", agent_name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        span.add_event("agent.request", req.model_dump())


        ctx = trace.set_span_in_context(span)
        resp = await chain_fn(req, ctx)


        span.add_event("agent.response", resp.model_dump())
        return resp
