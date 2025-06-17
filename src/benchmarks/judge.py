from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from agents import Agent

from .common import AgentRequest, AgentResponse, add_event, run_in_root, run_with_tracing


story_outline_generator = Agent(
    name="story_outline_generator",
    model="gpt-4o",
    instructions=(
        "You generate a very short story outline based on the user's input."
        "If there is any feedback provided, use it to improve the outline."
    ),
)


@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]


evaluator = Agent[None](
    name="evaluator",
    model="gpt-4o",
    instructions=(
        "You evaluate a story outline and decide if it's good enough."
        "If it's not good enough, you provide feedback on what needs to be improved."
        "Give it a pass at the third try at max."
    ),
    output_type=EvaluationFeedback,
)


async def _chain(req: AgentRequest, ctx) -> AgentResponse:
    prompt = req.prompt
    latest_outline: str | None = None
    feedback: str | None = None
    attempts = 0

    while True:
        outline_resp = await run_with_tracing(
            "judge.outline",
            story_outline_generator,
            AgentRequest(prompt=prompt if not feedback else f"{prompt}\nFeedback: {feedback}"),
            context=ctx,
        )
        latest_outline = outline_resp.output
        add_event("judge.outline_result", {"outline": latest_outline})

        eval_resp = await run_with_tracing(
            "judge.evaluate",
            evaluator,
            AgentRequest(prompt=latest_outline),
            context=ctx,
        )
        try:
            result = EvaluationFeedback.model_validate_json(eval_resp.output)
        except Exception:
            result = EvaluationFeedback(feedback=eval_resp.output, score="needs_improvement")
        add_event(
            "judge.evaluation_result",
            {
                "feedback": result.feedback,
                "score": result.score,
            },
        )

        attempts += 1
        if result.score == "pass" or attempts >= 5:
            break

        feedback = result.feedback

    return AgentResponse(output=latest_outline or "")


async def run(req: AgentRequest) -> AgentResponse:
    return await run_in_root(
        "judge",
        req,
        agent_name="judge_loop",
        chain_fn=_chain,
    )