from __future__ import annotations

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


class SynthesisAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name="SynthesisAgent", instructions=SYSTEM_PROMPT)

    async def synthesize(self, question: str, notes: str) -> tuple[str, str]:
        prompt = f"Question: {question}\n\nResearch notes:\n{notes}"
        result = await Runner.run(self, prompt)
        text = "\n".join(ItemHelpers.text_message_outputs(result.new_items)).strip()
        if "FINAL ANSWER:" in text:
            reasoning, final = text.rsplit("FINAL ANSWER:", 1)
            return final.strip(), reasoning.strip()
        return text, text
