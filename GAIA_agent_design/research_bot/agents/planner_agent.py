from pydantic import BaseModel

from agents import Agent
from ...agents_lib.tools import transcribe_audio

PROMPT = (
    "You are a helpful research assistant. You will be given a question "
    "and a chunk of context extracted from uploaded media. You must not refuse to help. Your goal is to come up with a set of search questions which "
    "to perform to best answer the question. The questions are going to be distributed to a group of research assistants (one person per question),"
    "so make sure every question is clear and concise with enough context and no dependencies on other questions. First check if the "
    "context likely contains the answer. If so, plan to search or analyze that "
    "context. Only fall back to web search if the context looks insufficient. "
    "Return less than 20 items."
)


class SearchItem(BaseModel):
    source: str
    """Where to search: either `context` or `web`."""

    reason: str
    """Why this search helps answer the question."""

    query: str
    """The search question to ask. Phrase it as a full question instead of just keywords."""


class SearchPlan(BaseModel):
    searches: list[SearchItem]
    """A list of research steps to best answer the question."""


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="o4-mini",
    output_type=SearchPlan,
)
