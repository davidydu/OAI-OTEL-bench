from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You plan research steps for another agent. You will be given a question "
    "and a chunk of context extracted from uploaded media. First check if the "
    "context likely contains the answer. If so, plan to search or analyse that "
    "context. Only fall back to web search if the context looks insufficient. "
    "For each step output a JSON item with three fields:\n"
    "- `source`: `context` or `web`\n"
    "- `reason`: why this step is needed\n"
    "- `query`: the search string or key phrase.\n"
    "Return between 1 and 10 items."
)


class SearchItem(BaseModel):
    source: str
    """Where to search: either `context` or `web`."""

    reason: str
    """Why this search helps answer the question."""

    query: str
    """The query or keyword for the search."""


class SearchPlan(BaseModel):
    searches: list[SearchItem]
    """A list of research steps to best answer the question."""


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="gpt-4.1",
    output_type=SearchPlan,
)
