from __future__ import annotations

from agents import WebSearchTool


def get_web_search_tool(user_location: dict | None = None) -> WebSearchTool:
    """Return a configured WebSearchTool."""
    return WebSearchTool(user_location=user_location or {"type": "approximate", "city": "New York"})
