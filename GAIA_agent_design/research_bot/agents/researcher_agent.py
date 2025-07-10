from agents import Agent, function_tool
from agents.model_settings import ModelSettings
from gpt_researcher import GPTResearcher

INSTRUCTIONS = (
    "You are a dedicated research assistant. Given a question "
    "and optional context, come up with a corresponding set of queries that closely adhere to the original question "
    "to perform to best answer the question. Then gather information relevant to answering each query faithfully without extra fluff. "
    "Do not attempt to come up with a solution to the original question. Only gather information needed to answer the question. Return the entire report."
)

@function_tool
async def run_gpt_research(task: str, context: str = "") -> str:
    """Run GPTResearcher on the given task and context."""
    query = task
    if context:
        query += f"\n\nContext:\n{context}"
    researcher = GPTResearcher(query=query)
    await researcher.conduct_research()
    return await researcher.write_report()

research_agent = Agent(
    name="ResearchAgent",
    instructions=INSTRUCTIONS,
    tools=[run_gpt_research],
    model_settings=ModelSettings(tool_choice="required"),
    model="o3",
)