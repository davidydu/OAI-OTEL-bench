from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are a world-class professor. You will be given the original question, any context "
    "from media files, and summaries of research your research assistants have provided. "
    "Use only the provided information to reason about the provided information and the question provided carefully, "
    "then finish your answer. You must follow the structured output format. Put your answer in the \"answer\" field and your reason in the \"reasoning\" field. "
    "Your answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. "
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
    model="o3",
    output_type=AnswerData,
)