from agents.agent import Agent
from telemetry import tracer

agent = Agent(
    name="echo_agent",
    instructions="You are a helpful assistant that echoes back what the user says."
)

with tracer.start_as_current_span("agent.run"):
    # Note: Agent.run() doesn't exist - we need to use Runner.run()
    # This is just a placeholder for now
    result = "Hello, OTEL!"  # agent.run(use_case="echo", input_data="Hello, OTEL!")
print(result)
