from agents import Agent, Runner
from agents.mcp import MCPServer

class FileReaderAgent(Agent):
    def __init__(self, mcp_server: MCPServer):
        super().__init__(
            name="FileReaderAgent",
            instructions="""
You have two tools available:

• list_directory(path) → JSON list of filenames  
• read_file(path)      → raw bytes or text of the file

When given a GAIA task_id, find all files under "./gaia_media" that start with that task_id.
If it’s a JSONL file, return the matching JSON line as text;
otherwise (image/audio), return the raw bytes.

Output ONLY the file’s contents—no extra commentary.
""",
            mcp_servers=[mcp_server],
        )

    def read_for(self, task_id: str) -> str:
        # kick off a single-run with our instructions + the task_id
        prompt = (
            f"Task ID: {task_id}\n"
            "List files in './gaia_media' and read the one for this ID."
        )
        result = Runner.run_sync(starting_agent=self, input=prompt)
        return result.final_output
