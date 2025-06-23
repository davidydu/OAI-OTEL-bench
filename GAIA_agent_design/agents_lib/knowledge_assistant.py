from __future__ import annotations

from agents import Agent

from .tools.web_search_tool import get_web_search_tool
from .tools.file_search_tool import get_file_search_tool

ASSISTANT_PROMPT = """
You are a research assistant helping to answer GAIA benchmark questions.
Use the available tools to search the web or local files for facts related to the
question and context provided. Summarize your findings as short bullet points.
Do not attempt to produce the final answer.
""".strip()


class KnowledgeAssistantAgent(Agent):
    def __init__(self) -> None:
        tools = [get_web_search_tool()]
        fs = get_file_search_tool()
        if fs is not None:
            tools.append(fs)
        super().__init__(name="KnowledgeAssistant", instructions=ASSISTANT_PROMPT, tools=tools)
