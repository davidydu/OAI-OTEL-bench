from __future__ import annotations

from agents import Agent, Runner, ItemHelpers

from .tools.web_search_tool import get_web_search_tool
from .tools.file_search_tool import get_file_search_tool


KNOWLEDGE_PROMPT = """
You are the KnowledgeAgent. Answer the user question using the provided context
and optional web or file searches.
Follow a Plan → Act → Reflect loop:
1. PLAN what information you need.
2. ACT by calling WebSearchTool or FileSearchTool as needed.
3. REFLECT on the results and update your plan.
When you are confident, conclude with:
FINAL ANSWER: <your answer>
""".strip()


class KnowledgeAgent(Agent):
    def __init__(self) -> None:
        tools = [get_web_search_tool()]
        file_search = get_file_search_tool()
        if file_search is not None:
            tools.append(file_search)
        super().__init__(name="KnowledgeAgent", instructions=KNOWLEDGE_PROMPT, tools=tools)

    async def answer(self, question: str, context: str) -> tuple[str, str]:
        """Run the agent asynchronously and return the final answer and reasoning."""
        prompt = f"Question: {question}\n\nContext:\n{context}"
        result = await Runner.run(self, prompt)
        text = "\n".join(ItemHelpers.text_message_outputs(result.new_items)).strip()
        if "FINAL ANSWER:" in text:
            reasoning, final = text.rsplit("FINAL ANSWER:", 1)
            return final.strip(), reasoning.strip()
        return text, text
