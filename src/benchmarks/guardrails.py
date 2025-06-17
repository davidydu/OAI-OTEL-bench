from __future__ import annotations

from typing import List

from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
)

from .common import AgentRequest, AgentResponse, run_with_tracing


class MathHomeworkOutput(BaseModel):
    reasoning: str
    is_math_homework: bool


guardrail_agent = Agent(
    name="guardrail_checker",
    model="gpt-4o",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    input: str | List[TResponseInputItem],
) -> GuardrailFunctionOutput:
    # Extract the last user message text
    if isinstance(input, str):
        text = input
    else:
        text = input[-1]["content"] if input else ""

    resp = await run_with_tracing(
        "guardrails.check",
        guardrail_agent,
        AgentRequest(prompt=text),
        context=context.context,
    )
    output = MathHomeworkOutput.model_validate_json(resp.output)
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_math_homework,
    )


async def run(req: AgentRequest) -> AgentResponse:
    agent = Agent(
        name="customer_support_agent",
        model="gpt-4o",
        instructions="You are a customer support agent.",
        input_guardrails=[math_guardrail],
    )
    try:
        return await run_with_tracing("guardrails", agent, req)
    except InputGuardrailTripwireTriggered:
        return AgentResponse(output="Sorry, I can't help you with your math homework.")