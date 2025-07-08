# from __future__ import annotations

# from agents import Agent
# from agents.model_settings import ModelSettings

# from ...agents_lib.tools import azure_task_adherence, VerificationResult

# __all__ = ["VerificationResult", "verifier_agent"]

# verifier_agent = Agent(
#     name="VerifierAgent",
#     instructions=(
#         "You receive a JSON payload with query and response messages. "
#         "Call the azure_task_adherence tool using that JSON as arguments and "
#         "return the result."
#     ),
#     tools=[azure_task_adherence],
#     model="gpt-4o-mini",
#     model_settings=ModelSettings(tool_choice="required"),
#     tool_use_behavior="stop_on_first_tool",
#     output_type=VerificationResult,
# )
