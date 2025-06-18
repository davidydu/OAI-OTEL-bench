import logfire
from agents import Agent, Runner

logfire.configure()
logfire.instrument_httpx()
logfire.instrument_openai_agents()

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(
    agent, 
    "Write a haiku about recursion in programming.")
print(result.final_output)