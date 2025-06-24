from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a GAIA writer agent. You will be given the original question, any context "
    "from GAIA media, and summaries of research you have performed. "
    "Write a short reasoning trace explaining how the evidence leads to the answer, "
    "then finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]. "
    "YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. "
    "If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. \
    If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. \
    If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."
)


class AnswerData(BaseModel):
    reasoning: str
    """Step-by-step reasoning leading to the final answer."""

    answer: str
    """The final answer to return."""


writer_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    model="gpt-4.1",
    output_type=AnswerData,
)
