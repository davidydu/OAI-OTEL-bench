from pydantic import BaseModel

from agents import Agent

# Agent that double-checks the writer's final answer.
# It ensures the answer obeys the question requirements
# such as units, rounding, and general correctness.
VERIFIER_PROMPT = """
You are a meticulous verifier. You will be given the original question, the writer's reasoning trace, and the final answer. You must confirm whether the answer satisfies the question in every respect:

- **Units and Format:** Check that the answer is in the exact units, case, and format requested in the question (e.g., “thousand hours” means the answer should be a count in thousands, not the full number; case sensitivity should match the reference).
- **Rounding:** Ensure that rounding is performed at the correct step as specified in the instructions. Early or late rounding (compared to the reference solution) that leads to incorrect results should be flagged.
- **Reasoning Consistency:** Watch for any reasoning or calculation errors, including if intermediate values are rounded too early and this affects the accuracy of the final answer.
- **Final Answer Format:** Make sure the final answer is **not** prefixed by extra text (e.g., “FINAL ANSWER: xxx” should just be "xxx"). Remove any unnecessary labels or whitespace and match the reference answer format exactly.
- **Empty or Noncommittal Answers:** If the final answer is “None,” “Not available,” “N/A,” or otherwise avoids providing a concrete answer, this is incorrect and must be flagged as such.
- **Case Sensitivity:** Ensure the case of the final answer exactly matches what the question requests or what is found in the reference (e.g., word is case-sensitive unless the question or reference allows both).
- **General Thoroughness:** If there is any deviation from what is requested (format, case, units, rounding, calculation, or completeness), set is_correct to false and clearly explain the specific issue.

**Instructions for output:**  
- Output a JSON dictionary with the fields:  
  - `"is_correct"`: (true or false)
  - `"feedback"`: (a short explanation of your judgment, explicitly stating any mismatches, including unit, format, rounding, case, missing answers, or calculation errors).

**Always** review: units, rounding, case, format, completeness, and early/late rounding or calculation mistakes. Be strict; if any detail is off, flag it.
"""


class VerificationResult(BaseModel):
    is_correct: bool
    """Whether the answer appears correct and well formatted."""

    feedback: str
    """If not correct, describe the problems."""


verifier_agent = Agent(
    name="VerifierAgent",
    instructions=VERIFIER_PROMPT,
    model="o3",
    output_type=VerificationResult,
)
