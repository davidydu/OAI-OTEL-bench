from __future__ import annotations

import re

from agents import Agent, Runner, ItemHelpers

SYSTEM_PROMPT = """
You are a general AI assistant. I will ask you a question. \
Report your thoughts, and finish your answer with the following template:

FINAL ANSWER: [YOUR FINAL ANSWER]

YOUR FINAL ANSWER should be a number OR as few words as possible OR \
a comma separated list of numbers and/or strings. If you are asked for \
a number, don't use commas or units (like $ or %). If you are asked for \
a string, don't use articles or abbreviations, and write digits in plain text.
""".strip()

from .tools.web_search_tool import get_web_search_tool


class VerifierAgent(Agent):
    """Fact-check answers by re-searching key entities."""

    def __init__(self) -> None:
        super().__init__(
            name="VerifierAgent",
            instructions=(
                "Given an answer and a list of entities, verify the factual correctness "
                "using web search and respond with one short sentence."
            ),
            tools=[get_web_search_tool()],
        )
        self.formatter = Agent(
            name="AnswerFormatter",
            instructions=SYSTEM_PROMPT,
        )
        
    @staticmethod
    def _clean_text(text: str) -> str:
        """Collapse whitespace for cleaner prompts."""
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    async def format_answer(self, question: str, answer: str) -> str:
        """Ensure final answer follows the system prompt."""
        prompt = f"Question: {question}\n\nCandidate answer:\n{answer}"
        result = await Runner.run(self.formatter, prompt)
        text = "\n".join(ItemHelpers.text_message_outputs(result.new_items)).strip()
        if "FINAL ANSWER:" in text:
            _, final = text.rsplit("FINAL ANSWER:", 1)
            return final.strip()
        return text
    
    async def verify(self, text: str) -> str:
        """Run fact checking asynchronously."""
        entities = re.findall(r"\b[A-Z][A-Za-z0-9]+(?: [A-Z][A-Za-z0-9]+)*\b", text)
        unique = ", ".join(sorted(set(entities)))
        if not unique:
            return "Verified: no entities found"
        prompt = (
            f"Answer: {text}\nEntities: {unique}\nCheck these entities and summarize in one short sentence."
        )
        result = await Runner.run(self, prompt)
        return f"Verified: {result.final_output.strip()}"

    async def choose_best(self, answers: list[str]) -> int:
        """Given multiple candidate answers, pick the best one.

        Returns the index of the preferred answer.
        """
        bullet_list = "\n".join(
            f"Option {i+1}: {a}" for i, a in enumerate(answers)
        )
        prompt = (
            "Evaluate the following candidate answers using web search and "
            "respond with the number of the best option.\n" + bullet_list
        )
        result = await Runner.run(self, prompt)
        try:
            return int(result.final_output.strip()) - 1
        except Exception:
            return 0
