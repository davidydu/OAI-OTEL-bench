from __future__ import annotations

from agents import Agent, ItemHelpers, MessageOutputItem
from opentelemetry import trace

from .common import AgentRequest, AgentResponse, run_with_tracing, run_in_root


spanish_agent = Agent(
    name="spanish_agent",
    model="gpt-4o",
    instructions="You translate the user's message to Spanish",
    handoff_description="An english to spanish translator",
)

french_agent = Agent(
    name="french_agent",
    model="gpt-4o",
    instructions="You translate the user's message to French",
    handoff_description="An english to french translator",
)

italian_agent = Agent(
    name="italian_agent",
    model="gpt-4o",
    instructions="You translate the user's message to Italian",
    handoff_description="An english to italian translator",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="gpt-4o",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools in order."
        "You never translate on your own, you always use the provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
        italian_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="Translate the user's message to Italian",
        ),
    ],
)

synthesizer_agent = Agent(
    name="synthesizer_agent",
    model="gpt-4o",
    instructions=(
        "You inspect translations, correct them if needed, and produce a final concatenated response."
    ),
)


async def _chain(req: AgentRequest, ctx) -> AgentResponse:
    root_span = trace.get_current_span()

    orch_resp, orch_result = await run_with_tracing(
        "tools.orchestrator",
        orchestrator_agent,
        req,
        context=ctx,
        return_result=True,
    )

    # steps = []
    # for item in getattr(orch_result, "new_items", []):
    #     if isinstance(item, MessageOutputItem):
    #         text = ItemHelpers.text_message_output(item)
    #         if text:
    #             steps.append(text)
    # if steps and root_span.is_recording():
    #     root_span.add_event("tools.translation.steps", {"steps": steps})

    synth_req = AgentRequest(prompt=orch_result.to_input_list())
    return await run_with_tracing(
        "tools.synthesizer",
        synthesizer_agent,
        synth_req,
        context=ctx,
    )


async def run(req: AgentRequest) -> AgentResponse:
    return await run_in_root(
        "tools",
        req,
        agent_name="tools_orchestrator",
        chain_fn=_chain,
    )