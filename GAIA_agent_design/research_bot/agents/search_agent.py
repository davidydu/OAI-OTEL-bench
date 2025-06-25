from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings

from ...agents_lib.tools.file_search_tool import get_file_search_tool
from ...agents_lib.tools.code_interpreter import get_code_interpreter_tool

INSTRUCTIONS = (
    "You are a research assistant with multiple tools. You may search the web or "
    "analyse provided context. If the input source is `context`, use the FileSearchTool "
    "and CodeInterpreterTool on the given text to find relevant information. "
    "If the source is `web`, use the WebSearchTool. Summarize the most important "
    "findings in under 300 words without extra fluff."
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
    model="gpt-4.1",
)
