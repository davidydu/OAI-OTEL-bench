from __future__ import annotations

from agents import FileSearchTool


def get_file_search_tool(max_num_results: int = 5, vector_store_ids: list[str] | None = None,
                         include_search_results: bool = False) -> FileSearchTool:
    """Return a configured FileSearchTool."""
    return FileSearchTool(
        max_num_results=max_num_results,
        vector_store_ids=vector_store_ids or [],
        include_search_results=include_search_results,
    )
