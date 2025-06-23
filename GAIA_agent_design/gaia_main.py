"""Entry point exposing the GAIA system prompt."""

from agents import Agent

SYSTEM_PROMPT = """
You are a general AI assistant. I will ask you a question. \
Report your thoughts, and finish your answer with the following template:

FINAL ANSWER: [YOUR FINAL ANSWER]

YOUR FINAL ANSWER should be a number OR as few words as possible OR \
a comma separated list of numbers and/or strings. If you are asked for \
a number, don't use commas or units (like $ or %). If you are asked for \
a string, don't use articles or abbreviations, and write digits in plain text.
"""

agent = Agent(name="GAIA Assistant", instructions=SYSTEM_PROMPT.strip())

if __name__ == "__main__":
    import sys
    from agents import Runner, ItemHelpers

    if len(sys.argv) != 2:
        print("Usage: python gaia_main.py 'Your question'")
        raise SystemExit(1)

    result = Runner.run_sync(agent, sys.argv[1])
    output = "\n".join(ItemHelpers.text_message_outputs(result.new_items))
    print(output)
