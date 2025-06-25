from pydantic import BaseModel

from agents import Agent

from .planner_agent import SearchItem, SearchPlan

INSTRUCTIONS = (
    "You review search summaries and any verifier feedback to decide if more "
    "research is required. If the current evidence from context is insufficient, "
    "propose new items to search either in the `context` or on the `web`. Each "
    "item must follow the same format as the planner output (source, reason, "
    "query). Return an empty list when no further searches are needed."
)


evaluator_agent = Agent(
    name="EvaluatorAgent",
    instructions=INSTRUCTIONS,
    output_type=SearchPlan,
    model="gpt-4.1",
)
