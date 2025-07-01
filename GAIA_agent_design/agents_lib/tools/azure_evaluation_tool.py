from __future__ import annotations

import asyncio
import os
import json
from typing import List, Optional

from pydantic import BaseModel
from agents import function_tool
from azure.ai.evaluation import TaskAdherenceEvaluator
from azure.ai.evaluation._model_configurations import OpenAIModelConfiguration

__all__ = [
    "MessageContent",
    "Message",
    "VerificationResult",
    "azure_task_adherence",
]

_oai_model_config = OpenAIModelConfiguration(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1",
    model="o4-mini",
    type="openai",
)

_evaluator = TaskAdherenceEvaluator(
    model_config=_oai_model_config,
    is_reasoning_model=True,
)


class MessageContent(BaseModel):
    type: str
    text: str


class Message(BaseModel):
    role: str
    content: List[MessageContent]


class VerificationResult(BaseModel):
    score: int
    feedback: str
    is_correct: bool


@function_tool
async def azure_task_adherence(
    query: List[Message],
    response: List[Message],
    tool_definitions: Optional[str] = None,
) -> VerificationResult:
    """Run Azure Task Adherence evaluator and return a score and feedback."""
    result = await asyncio.to_thread(
        _evaluator,
        query=[m.model_dump() for m in query],
        response=[m.model_dump() for m in response],
        tool_definitions=None if tool_definitions is None else json.loads(tool_definitions),
    )
    score = int(result.get("task_adherence", 0))
    feedback = result.get("task_adherence_reason", "")
    return VerificationResult(score=score, feedback=feedback, is_correct=score >= 3)