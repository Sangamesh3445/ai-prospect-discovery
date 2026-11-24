
def build_search_query(base_query: str) -> str:
    """Build a search query for publicly published contact information."""

    if not isinstance(base_query, str) or not base_query.strip():
        raise ValueError("Search query cannot be empty.")

    return (
        f'{base_query.strip()} '
        f'("email" OR "contact" OR "contact us")'
    )
