from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings

from ...agents_lib.tools.file_search_tool import get_file_search_tool
from ...agents_lib.tools.code_interpreter import get_code_interpreter_tool

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term "
    "and summarize the most relevant results. Keep the summary under 300 words. Grammar is not important, don't add extra fluff."
)

TOOLS = [WebSearchTool()]
file_search = get_file_search_tool()
if file_search is not None:
    TOOLS.append(file_search)
TOOLS.append(get_code_interpreter_tool())

search_agent = Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=TOOLS,
    model_settings=ModelSettings(tool_choice="required"),
    model="gpt-4.1"
)
