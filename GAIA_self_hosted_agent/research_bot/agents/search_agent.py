from agents import Agent, Runner, function_tool
from agents.model_settings import ModelSettings
from ... import sglang_client

# from ...agents_lib.tools.file_search_tool import get_file_search_tool
# from ...agents_lib.tools.code_interpreter import get_code_interpreter_tool

# from gpt_researcher import GPTResearcher
from browser_use.llm import ChatOpenAI
from browser_use import Agent as BrowserUseAgent

INSTRUCTIONS = (
    "You are a research assistant with a web research tool. You may be given a context that is processed from another tool or an LLM. According to the 'source' field, you must either use the tool to search the web or "
    "analyze provided context (if source is a file, it will be extracted as the context)."
    "When searching web, you must use the research tool to gather information until it is sufficient to answer the query."
    "To use the research tool, give the run_gpt_researcb function a clear, concise query with enough context. Do not use the tools for more than 3 times."
    "If 'source' field is 'context', you must not use the search tool and only analyze the provided context."
    "Summarize the most important findings in under 300 words without extra fluff."
)

TOOLS = []

# @function_tool
# async def run_gpt_research(query: str, source: str = "web") -> str:
#     """Use GPTResearcher for deeper research on a topic."""
#     researcher = GPTResearcher(query=query, report_source=source)
#     await researcher.conduct_research()
#     return await researcher.write_report()

# TOOLS.append(run_gpt_research)

@function_tool
async def run_browser_research(query: str) -> str:
    llm = ChatOpenAI(
        model = sglang_client.SGLANG_MODEL
    )
    browser_use_agent = BrowserUseAgent(
        task = query,
        llm = llm,
    )
    result = await browser_use_agent.run()
    return result or ""

TOOLS.append(run_browser_research)




    

search_agent = Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=TOOLS,
    model_settings=ModelSettings(),
    model=sglang_client.SGLANG_MODEL,
)
