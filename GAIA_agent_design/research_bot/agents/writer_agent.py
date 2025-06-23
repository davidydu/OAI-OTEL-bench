from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a GAIA writer agent. You will be given the original question, any context "
    "from GAIA media, and summaries of research you have performed. "
    "Write a short reasoning trace explaining how the evidence leads to the answer, "
    "then provide the final answer after 'FINAL ANSWER:'."
)


class AnswerData(BaseModel):
    reasoning: str
    """Step-by-step reasoning leading to the final answer."""

    answer: str
    """The final answer to return."""


writer_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    model="o3-mini",
    output_type=AnswerData,
)
