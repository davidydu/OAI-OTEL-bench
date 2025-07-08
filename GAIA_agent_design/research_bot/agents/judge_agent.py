from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You evaluate answers from multiple writer agents. "
    "Given the original question, any media context, summaries of research, "
    "and each writer's reasoning and answer, decide if the writers agree on the final answer. "
    " Two answers are judged equal if, after normalization, they match in one of three ways: " 
    " 1) Numeric—both can be parsed as numbers once $, %, and commas are stripped, and the resulting floats are exactly equal; "
    " 2) List—ground-truth contains “,” or “;”, so both answers are split on these delimiters, must have the same length, and each corresponding element must match either numerically (per rule 1) or textually after lower-casing and removing all whitespace while keeping punctuation; " 
    " 3) String—otherwise, both answers match when all whitespace and punctuation are removed and the remainder is compared case-insensitively. "
    " If the answer is `None`, treat it as the literal string 'None' before applying these rules. "
    "If they agree, return `consensus: true` and provide the agreed answer in `final_answer`. "
    "If they do not agree, decide if it is clear which answer is correct. If so, provide the agreed answer in `final_answer`. If not, return `consensus: false` and provide feedback to help the writers converge." 
)


class JudgeResult(BaseModel):
    consensus: bool
    final_answer: str | None
    feedback: str | None


judge_agent = Agent(
    name="JudgeAgent",
    instructions=PROMPT,
    model="o4-mini",
    output_type=JudgeResult,
)