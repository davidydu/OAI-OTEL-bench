from agents import WebSearchTool


def get_web_search_tool(user_location: dict = None) -> WebSearchTool:
    """
    Factory function to create a configured WebSearchTool.

    Args:
        user_location: A dict containing location hints, e.g.
            {"type": "approximate", "city": "New York"}
            If None, defaults to no location filter.

    Returns:
        An instance of WebSearchTool ready to be passed into an Agent.
    """
    # Default to no location constraint if not provided
    if user_location is None:
        user_location = {"type": "approximate", "city": "New York"}

    return WebSearchTool(user_location=user_location)


from agents import FileSearchTool

def get_file_search_tool(max_num_results: int = 5,
                         vector_store_ids: list[str] | None = None,
                         include_search_results: bool = False) -> FileSearchTool:
    """
    Factory for FileSearchTool.

    Args:
        max_num_results: number of results to return.
        vector_store_ids: list of vector store IDs to query.
        include_search_results: whether to include raw text in output.
    Returns:
        Configured FileSearchTool instance.
    """
    return FileSearchTool(
        max_num_results=max_num_results,
        vector_store_ids=vector_store_ids or [],
        include_search_results=include_search_results,
    )

