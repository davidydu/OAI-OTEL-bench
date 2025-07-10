# from pydantic import BaseModel

# from agents import Agent

# from .planner_agent import SearchItem, SearchPlan

# INSTRUCTIONS = (
#     "Given a question and research summaries from research assistants, you review search summaries and decide if more research is required. "
#     "If the summaries from the provided context seem insufficient, propose new "
#     "items to search either in the `context` or on the `web`. The questions are going to be distributed to a group of research assistants (one person per question),"
#     "so make sure every question is clear and concise with enough context and no dependencies on other questions. Each item should "
#     "follow the same format as the planner output (source, reason, query). "
#     "Return an empty list when no further searches are needed."
# )


# evaluator_agent = Agent(
#     name="EvaluatorAgent",
#     instructions=INSTRUCTIONS,
#     output_type=SearchPlan,
#     model="o4-mini",
# )
