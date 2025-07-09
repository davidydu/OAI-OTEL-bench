from pydantic import BaseModel

from agents import Agent

SAMPLE_REVISION_NOTES = """
{
  "draft": "The revised draft that you are submitting for review",
  "revision_notes": "Your message to the reviewer about the changes you made to the draft based on their feedback"
}
"""


def build_reviser_prompt(draft: str, review: str) -> str:
    """Return the user prompt for :data:`reviser_agent`."""
    return (
        f"Draft:\n{draft}\nReviewer's notes:\n{review}\n\n"
        "You have been tasked by your reviewer with revising the following draft, which was written by a non-expert.\n"
        "If you decide to follow the reviewer's notes, please write a new draft and make sure to address all of the points they raised.\n"
        "Please keep all other aspects of the draft the same.\n"
        "You MUST return nothing but a JSON in the following format:\n"
        f"{SAMPLE_REVISION_NOTES}"
    )


class RevisionData(BaseModel):
    draft: str
    revision_notes: str


reviser_agent = Agent(
    name="ReviserAgent",
    instructions="You are an expert writer. Your goal is to revise drafts based on reviewer notes.",
    model="o4-mini",
    output_type=RevisionData,
)