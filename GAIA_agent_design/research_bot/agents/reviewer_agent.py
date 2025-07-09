from typing import Sequence

from agents import Agent

TEMPLATE = (
    "You are an expert research article reviewer. "
    "Your goal is to review research drafts and provide feedback to the reviser only based on specific guidelines."
)


def build_review_prompt(draft: str, guidelines: Sequence[str], revision_notes: str | None = None) -> str:
    """Return the user prompt for :data:`reviewer_agent`."""
    guidelines_text = "\n- ".join(guidelines)
    if guidelines_text:
        guidelines_text = "- " + guidelines_text
    revise_prompt = (
        "The reviser has already revised the draft based on your previous review notes with the following feedback:\n"
        f"{revision_notes}\n"
        "Please provide additional feedback ONLY if critical since the reviser has already made changes based on your previous feedback.\n"
        "If you think the article is sufficient or that non critical revisions are required, please aim to return None.\n"
    ) if revision_notes else ""
    return (
        "You have been tasked with reviewing the research draft which was written by a non-expert based on specific guidelines.\n"
        "Please accept the draft if it is good enough, or send it for revision, along with your notes to guide the revision.\n"
        "If not all of the guideline criteria are met, you should send appropriate revision notes.\n"
        "If the draft meets all the guidelines, please return None.\n"
        f"{revise_prompt}"
        f"Guidelines:\n{guidelines_text}\nDraft: {draft}"
    )


reviewer_agent = Agent(
    name="ReviewerAgent",
    instructions=TEMPLATE,
    model="o4-mini",
)