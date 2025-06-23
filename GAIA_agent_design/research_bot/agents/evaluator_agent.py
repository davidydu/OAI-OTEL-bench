from pydantic import BaseModel

from agents import Agent

from .planner_agent import WebSearchItem, WebSearchPlan

INSTRUCTIONS = (
    "You are an evaluation agent. Review the search summaries and decide if more information is needed "
    "to answer the question. If additional searches are required, propose up to 5 search terms. "
    "Return an empty list if no further searches are necessary."
)


evaluator_agent = Agent(
    name="EvaluatorAgent",
    instructions=INSTRUCTIONS,
    output_type=WebSearchPlan,
    model="o3-mini",
)
