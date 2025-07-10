from pydantic import BaseModel

from agents import Agent
from ...agents_lib.tools import transcribe_audio

PROMPT = (
    "You are a helpful leading research assistant. Given a question "
    "and optional context, come up with a corresponding set of queries that unbiasedly and closely adhere to the original question "
    "to perform to best answer the question. For each query, the source can be either 'context' or 'web'. The queries are going to be distributed to a group of research assistants (one person per question),"
    "so make sure every query is clear and concise with enough background information from the question and no dependencies on other queries. Each query should be as concise and relevant to the original question as possible. First check if the "
    "context likely contains the answer. If so, plan to search or analyze that "
    "context. Only fall back to web search if the context looks insufficient. "
    "Return less than 20 items. You must not refuse to help."
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
