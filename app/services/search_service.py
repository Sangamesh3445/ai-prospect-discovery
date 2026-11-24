
import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


class SearchServiceError(Exception):
    """Raised when prospect search fails."""


def search_web(query: str, max_results: int = 10) -> list:
    """Search publicly available web information using Tavily."""

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise SearchServiceError(
            "Search API key is not configured."
        )

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise ValueError("Maximum results must be an integer.")

    if not 1 <= max_results <= 20:
        raise ValueError("Maximum results must be between 1 and 20.")

    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=query.strip(),
            max_results=max_results,
            search_depth="basic",
        )

        results = response.get("results", [])

        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
            for item in results
            if item.get("url")
        ]

    except Exception as exc:
        raise SearchServiceError(
            "The web search request failed."
        ) from exc
