import os
import asyncio
from pydantic import BaseModel
import logfire
from agents import Agent as AgentsAgent, Runner, function_tool
from pydantic_ai import Agent as PydanticAgent
from opentelemetry import trace

# --- Pydantic models for structured I/O ---
class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    output: str

# --- Tool definition ---
FACTS = {
    "eiffel tower": "The Eiffel Tower is in Paris and was built in 1889.",
    "openai": "OpenAI is an AI research and deployment company.",
}

@function_tool
def lookup_fact(topic: str) -> str:
    return FACTS.get(topic.lower(), "No information available.")

# --- Helper decorator for automated span instrumentation ---
tracer = trace.get_tracer(__name__)

def trace_agent(use_case_name: str, model_name: str = None):
    """
    Decorator to trace agent use cases.
    Args:
      use_case_name: suffix for span name (use_case.<name>)
      model_name: explicit model identifier to add as attribute
    """
    def decorator(func):
        async def wrapper(agent, req: AgentRequest, *args, **kwargs):
            span_name = f"use_case.{use_case_name}"
            with tracer.start_as_current_span(span_name) as span:
                # Agent name attribute
                agent_name = getattr(agent, 'name', None)
                if isinstance(agent_name, str):
                    span.set_attribute("agent.name", agent_name)

                # Model name detection
                resolved_model = model_name or getattr(agent, 'model_name', None) or getattr(agent, 'model', None)
                if resolved_model is not None:
                    # convert non-string models to string
                    model_str = resolved_model if isinstance(resolved_model, str) else str(resolved_model)
                    span.set_attribute("model.name", model_str)

                # Instructions if provided
                instructions = getattr(agent, 'instructions', None)
                if isinstance(instructions, str):
                    span.set_attribute("agent.instructions", instructions)

                # Tools if provided
                tools = getattr(agent, 'tools', None)
                if isinstance(tools, (list, tuple)) and tools:
                    tool_names = []
                    for t in tools:
                        fn = getattr(t, '__wrapped__', t)
                        name = getattr(fn, '__name__', None)
                        if name:
                            tool_names.append(name)
                    if tool_names:
                        span.set_attribute("agent.tools", tool_names)

                # Structured I/O events
                span.add_event("agent.request", req.model_dump())

                # Execute the actual agent call
                if hasattr(agent, 'run') and callable(agent.run):
                    result = await agent.run(req.prompt)
                else:
                    result = await Runner.run(agent, input=req.prompt)

                # Response handling
                resp_value = getattr(result, 'final_output', None) or getattr(result, 'output', None)
                resp = AgentResponse(output=resp_value)
                span.add_event("agent.response", resp.model_dump())
            return resp
        return wrapper
    return decorator

# --- Instrumented agent runs ---

@trace_agent('echo')
async def run_echo(agent: AgentsAgent, req: AgentRequest) -> AgentResponse:
    return await Runner.run(agent, input=req.prompt)

@trace_agent('cot')
async def run_chain_of_thought(agent: AgentsAgent, req: AgentRequest) -> AgentResponse:
    return await Runner.run(agent, input=req.prompt)

@trace_agent('rag')
async def run_rag(agent: AgentsAgent, req: AgentRequest) -> AgentResponse:
    return await Runner.run(agent, input=req.prompt)

@trace_agent('pydantic')  # PydanticAgent captures its own model name
async def run_pydantic(agent: PydanticAgent, req: AgentRequest) -> AgentResponse:
    return await agent.run(req.prompt)

async def main() -> None:
    # Configure Logfire + instrumentation
    logfire.configure(token=os.getenv("LOGFIRE_TOKEN", "pylf_v1_us_9bZ57RDYs2P0LbbxcjK95kxZKL0jqFDhKqjYtTR7Wwy7"))
    logfire.instrument_openai_agents()
    logfire.instrument_pydantic_ai()

    # Ensure API key
    os.environ.setdefault("OPENAI_API_KEY", "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")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY in environment.")

    # Bind telemetry tracer after instrumentation
    import telemetry
    global tracer
    tracer = telemetry.tracer

    # Prepare agents and requests
    echo_agent = AgentsAgent(
        name="echo_agent",
        model="gpt-4o",  # specify model explicitly
        instructions="You are a helpful assistant that echoes back what the user says.",
    )
    cot_agent = AgentsAgent(
        name="cot_agent",
        model="o1",  # use a lighter model for chain-of-thought
        instructions="You are a reasoning assistant. Think step by step before answering.",
    )
    rag_agent = AgentsAgent(
        name="rag_agent",
        model="gpt-4o",  # RAG uses a standard GPT-4 model
        instructions="Use the lookup_fact tool to answer factual questions.",
        tools=[lookup_fact],
    )
    pyd_agent = PydanticAgent('openai:gpt-4o')

    echo_req = AgentRequest(prompt="Hello, OTEL!")
    cot_req = AgentRequest(prompt="If I have 2 apples and add 3, how many? Think step by step.")
    rag_req = AgentRequest(prompt="Tell me about the Eiffel Tower.")
    pyd_req = AgentRequest(prompt="How does pyodide let you run Python in the browser? (short answer please)")

    # Execute use cases
    print((await run_echo(echo_agent, echo_req)).output)
    print((await run_chain_of_thought(cot_agent, cot_req)).output)
    print((await run_rag(rag_agent, rag_req)).output)
    print((await run_pydantic(pyd_agent, pyd_req)).output)

if __name__ == "__main__":
    asyncio.run(main())