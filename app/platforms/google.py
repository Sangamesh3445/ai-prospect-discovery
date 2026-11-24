
def build_search_query(base_query: str) -> str:
    """Build a general web search query."""

    if not isinstance(base_query, str) or not base_query.strip():
        raise ValueError("Search query cannot be empty.")

    return base_query.strip()
