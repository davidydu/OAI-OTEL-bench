from __future__ import annotations

import re

from agents import Agent, Runner

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