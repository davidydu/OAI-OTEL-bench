from openai_agents.agent import Agent
from telemetry import tracer

agent = Agent(...)
with tracer.start_as_current_span("agent.run"):
    result = agent.run(use_case="echo", input_data="Hello, OTEL!")
print(result)
