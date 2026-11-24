
def build_search_query(base_query: str) -> str:
    """Build a search query for publicly indexed WhatsApp Business links."""

    if not isinstance(base_query, str) or not base_query.strip():
        raise ValueError("Search query cannot be empty.")

    return (
        f'(site:wa.me OR site:api.whatsapp.com '
        f'OR site:whatsapp.com) {base_query.strip()}'
    )
