from __future__ import annotations

from agents import Agent, Runner, ItemHelpers

SYNTHESIZER_PROMPT = """
You are a synthesizer agent. You will be given a question from the GAIA benchmark and \
research notes from a research assistant. Use the research notes as the sole information (if in the research notes a word is lowercase, don't make it uppercase in the final answer) to decide on the final answer \
in the following format: \

FINAL ANSWER: [YOUR FINAL ANSWER]

YOUR FINAL ANSWER should be a number OR as few words as possible OR \
a comma separated list of numbers and/or strings. If you are asked for \
a number, don't use commas or units (like $ or %). If you are asked for \
a string, don't use articles or abbreviations, and write digits in plain text.
""".strip()


class SynthesisAgent(Agent):
    def __init__(self) -> None:
        super().__init__(name="SynthesisAgent", instructions=SYNTHESIZER_PROMPT)

    async def synthesize(self, question: str, notes: str) -> tuple[str, str]:
        prompt = f"Question: {question}\n\nResearch notes:\n{notes}"
        result = await Runner.run(self, prompt)
        text = "\n".join(ItemHelpers.text_message_outputs(result.new_items)).strip()
        if "FINAL ANSWER:" in text:
            reasoning, final = text.rsplit("FINAL ANSWER:", 1)
            return final.strip(), reasoning.strip()
        return text, text
