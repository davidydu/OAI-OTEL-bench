from __future__ import annotations

from agents import Agent

from .tools.web_search_tool import get_web_search_tool
from .tools.file_search_tool import get_file_search_tool

RESEARCH_PROMPT = (
    "You are a research assistant. Use the available tools to search the web or files "
    "and provide concise factual notes that help answer the question. "
    "Do not attempt to give the final answer."
)


class ResearchAssistantAgent(Agent):
    def __init__(self, name: str) -> None:
        tools = [get_web_search_tool()]
        fs = get_file_search_tool()
        if fs is not None:
            tools.append(fs)
        super().__init__(name=name, instructions=RESEARCH_PROMPT, tools=tools)
