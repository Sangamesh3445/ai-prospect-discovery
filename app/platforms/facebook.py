
def build_search_query(base_query: str) -> str:
    """Build a search query for publicly indexed Facebook pages."""

    if not isinstance(base_query, str) or not base_query.strip():
        raise ValueError("Search query cannot be empty.")

    return f"site:facebook.com {base_query.strip()}"
