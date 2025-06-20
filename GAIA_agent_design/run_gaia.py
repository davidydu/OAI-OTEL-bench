import json
import os
import shutil
import logfire
from agents import Runner, trace, ItemHelpers
from agents.mcp import MCPServerStdio
from agents.file_reader import FileReaderAgent

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

def extract_trace_and_answer(items):
    texts = ItemHelpers.text_message_outputs(items)
    full = "\n".join(texts).strip()
    if "FINAL ANSWER:" in full:
        reasoning, final = full.rsplit("FINAL ANSWER:", 1)
        return final.strip(), reasoning.strip()
    return "", full

async def main(jsonl_path: str, out_path: str):
    # Ensure npx is installed
    if not shutil.which("npx"):
        raise RuntimeError("Install npx: `npm install -g npx`")

    media_dir = os.path.abspath("gaia_media")
    # 1) launch the filesystem MCP server
    async with MCPServerStdio(
        name="GAIA Filesystem",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", media_dir],
        },
    ) as mcp:

        # 2) build our file‐reader
        file_reader = FileReaderAgent(mcp)

        # 3) process each GAIA example
        with open(jsonl_path) as src, open(out_path, "w") as dst:
            for line in src:
                task = json.loads(line)
                tid = task["task_id"]
                q   = task["Question"]
                span = f"GAIA Question {tid}"

                with trace(span):
                    # → step 1: fetch file for this task_id
                    raw = file_reader.read_for(tid)

                    # (for now we just embed it as text; later you'll
                    #  detect binary vs. text and call a MediaProcessorAgent)
                    prompt = (
                        f"{q}\n\n"
                        "Here is the file contents from the media directory:\n"
                        f"{raw}\n\n"
                        "Report your thoughts and finish with:\n"
                        "FINAL ANSWER: [your answer]"
                    )

                    # → step 2: ask the original GAIA Assistant
                    from agents import Agent
                    gaia_agent = Agent(
                        name="GAIA Assistant",
                        instructions=SYSTEM_PROMPT.strip()
                    )
                    result = Runner.run_sync(starting_agent=gaia_agent, input=prompt)

                answer, trace_txt = extract_trace_and_answer(result.new_items)
                out = {
                    "task_id": tid,
                    "model_answer": answer,
                    "reasoning_trace": trace_txt,
                }
                dst.write(json.dumps(out, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    import sys, asyncio
    if len(sys.argv) != 3:
        print("Usage: python run_gaia.py metadata.jsonl submission.jsonl")
        sys.exit(1)
    # python run_gaia.py ./GAIA/2023/test/metadata.jsonl my_submission.jsonl
    asyncio.run(main(sys.argv[1], sys.argv[2]))