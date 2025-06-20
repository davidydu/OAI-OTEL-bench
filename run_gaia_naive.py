import json
import logfire
from agents import Agent, Runner, ItemHelpers, trace


logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()


SYSTEM_PROMPT = """
You are a general AI assistant. I will ask you a question. \
Report your thoughts, and finish your answer with the following template:

FINAL ANSWER: [YOUR FINAL ANSWER]

YOUR FINAL ANSWER should be a number OR as few words as possible OR \
a comma separated list of numbers and/or strings. If you are asked for \
a number, don't use commas or units (like $ or %). If you are asked for \
a string, don't use articles or abbreviations, and write digits in plain text.
"""

agent = Agent(
    name="GAIA Assistant",
    instructions=SYSTEM_PROMPT.strip(),
    model="o3"
)

def extract_trace_and_answer(items):
    """
    Given result.new_items from the Agent run, separate
    - reasoning_trace: the concatenated intermediate messages
    - model_answer: the text after 'FINAL ANSWER:'
    """
    texts = ItemHelpers.text_message_outputs(items)
    full = "\n".join(texts).strip()
    # Split on the FINAL ANSWER marker
    if "FINAL ANSWER:" in full:
        reasoning, final = full.rsplit("FINAL ANSWER:", 1)
        reasoning_trace = reasoning.strip()
        model_answer = final.strip()
    else:
        # fallback if the model didn’t follow instructions
        reasoning_trace = full
        model_answer = ""
    return model_answer, reasoning_trace

def run_gaia(jsonl_path: str, out_path: str):
    with open(jsonl_path) as src, open(out_path, "w") as dst:
        for line in src:
            task = json.loads(line)
            q = task["Question"]
            span_name = f"GAIA Question {task['task_id']}"
            # Wrap each question in its own trace span
            with trace(span_name):
                result = Runner.run_sync(agent, q)
            # Pull reasoning vs final
            model_answer, reasoning_trace = extract_trace_and_answer(result.new_items)
            # Write out the JSONL line
            out = {
                "task_id": task["task_id"],
                "model_answer": model_answer,
                "reasoning_trace": reasoning_trace,
            }
            dst.write(json.dumps(out, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python run_gaia_naive.py path/to/gaia.jsonl path/to/submission.jsonl")
        sys.exit(1)
    # python run_gaia.py ./GAIA/2023/test/metadata.jsonl my_submission.jsonl
    run_gaia(sys.argv[1], sys.argv[2])
