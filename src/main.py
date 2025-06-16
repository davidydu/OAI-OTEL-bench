import os
import asyncio
from pydantic import BaseModel
import logfire
from agents import Agent as AgentsAgent, Runner, function_tool
from pydantic_ai import Agent as PydanticAgent
from opentelemetry import trace


class AgentRequest(BaseModel):
    prompt: str


class AgentResponse(BaseModel):
    output: str


FACTS = {
    "eiffel tower": "The Eiffel Tower is in Paris and was built in 1889.",
    "openai": "OpenAI is an AI research and deployment company.",
}


@function_tool
def lookup_fact(topic: str) -> str:
    return FACTS.get(topic.lower(), "No information available.")


tracer = trace.get_tracer(__name__)


def trace_agent(use_case_name: str, model_name: str | None = None):
    """Decorator to trace agent use cases."""

    def decorator(func):
        async def wrapper(agent, req: AgentRequest, *args, **kwargs):
            span_name = f"use_case.{use_case_name}"
            with tracer.start_as_current_span(span_name) as span:
                agent_name = getattr(agent, "name", None)
                if isinstance(agent_name, str):
                    span.set_attribute("agent.name", agent_name)

                resolved_model = (
                    model_name
                    or getattr(agent, "model_name", None)
                    or getattr(agent, "model", None)
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
                resp = AgentResponse(output=resp_value)
                span.add_event("agent.response", resp.model_dump())
            return resp

        return wrapper

    return decorator


@trace_agent("echo")
async def run_echo(agent: AgentsAgent, req: AgentRequest) -> AgentResponse:
    return await Runner.run(agent, input=req.prompt)


@trace_agent("cot")
async def run_chain_of_thought(agent: AgentsAgent, req: AgentRequest) -> AgentResponse:
    return await Runner.run(agent, input=req.prompt)


@trace_agent("rag")
async def run_rag(agent: AgentsAgent, req: AgentRequest) -> AgentResponse:
    return await Runner.run(agent, input=req.prompt)


@trace_agent("pydantic")
async def run_pydantic(agent: PydanticAgent, req: AgentRequest) -> AgentResponse:
    return await agent.run(req.prompt)


async def main() -> None:
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
    logfire.instrument_openai_agents()
    logfire.instrument_pydantic_ai()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY in environment.")

    import telemetry

    global tracer
    tracer = telemetry.tracer

    echo_agent = AgentsAgent(
        name="echo_agent",
        model="gpt-4o",
        instructions="You are a helpful assistant that echoes back what the user says.",
    )
    cot_agent = AgentsAgent(
        name="cot_agent",
        model="o1",
        instructions="You are a reasoning assistant. Think step by step before answering.",
    )
    rag_agent = AgentsAgent(
        name="rag_agent",
        model="gpt-4o",
        instructions="Use the lookup_fact tool to answer factual questions.",
        tools=[lookup_fact],
    )
    pyd_agent = PydanticAgent("openai:gpt-4o")

    echo_req = AgentRequest(prompt="Hello, OTEL!")
    cot_req = AgentRequest(
        prompt="If I have 2 apples and add 3, how many? Think step by step."
    )
    rag_req = AgentRequest(prompt="Tell me about the Eiffel Tower.")
    pyd_req = AgentRequest(
        prompt="How does pyodide let you run Python in the browser? (short answer please)"
    )

    print((await run_echo(echo_agent, echo_req)).output)
    print((await run_chain_of_thought(cot_agent, cot_req)).output)
    print((await run_rag(rag_agent, rag_req)).output)
    print((await run_pydantic(pyd_agent, pyd_req)).output)


if __name__ == "__main__":
    asyncio.run(main())
