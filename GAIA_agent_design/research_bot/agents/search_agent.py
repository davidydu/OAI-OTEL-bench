from agents import Agent, WebSearchTool, function_tool
from agents.model_settings import ModelSettings
from gpt_researcher import GPTResearcher

from ...agents_lib.tools.file_search_tool import get_file_search_tool
from ...agents_lib.tools.code_interpreter import get_code_interpreter_tool

INSTRUCTIONS = (
    "You are a research assistant with multiple tools. You may search the web or "
    "analyze provided context (if source is a media file, it will be extracted as the context) as you see fit."
    "Summarize the most important findings in under 300 words without extra fluff."
    "When appropriate, such as doing web searches, you can run both the websearch tool and a deeper GPTResearcher search to gather more detailed information."
)

TOOLS = [WebSearchTool]
file_search = get_file_search_tool()
if file_search is not None:
    TOOLS.append(file_search)
TOOLS.append(get_code_interpreter_tool())

@function_tool
async def run_gpt_research(query: str, source: str = "web") -> str:
    """Use GPTResearcher for deeper research on a topic."""
    researcher = GPTResearcher(query=query, report_source=source)
    await researcher.conduct_research()
    return await researcher.write_report()

TOOLS.append(run_gpt_research)


search_agent = Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=TOOLS,
    model_settings=ModelSettings(tool_choice="required"),
    model="gpt-4.1",
)
