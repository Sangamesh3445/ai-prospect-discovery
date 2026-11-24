
from app.services.search_service import (
    search_web,
    SearchServiceError,
)
from app.services.profile_extractor import extract_profiles
from app.services.deduplication_service import deduplicate_profiles
from app.services.relevance_service import filter_relevant_profiles

from app.platforms import (
    google,
    linkedin,
    x_platform,
    youtube,
    instagram,
    facebook,
    threads,
    whatsapp,
    email,
)


PLATFORM_ADAPTERS = {
    "google": google,
    "linkedin": linkedin,
    "x": x_platform,
    "youtube": youtube,
    "instagram": instagram,
    "facebook": facebook,
    "threads": threads,
    "whatsapp": whatsapp,
    "email": email,
}


def discover_prospects(query_data: dict) -> dict:
    """Discover, extract, deduplicate and rank public prospects."""

    if not isinstance(query_data, dict):
        raise ValueError("Query data must be a dictionary.")

    platforms = query_data.get(
        "platforms",
        ["google", "linkedin"],
    )

    max_results = query_data.get("max_results", 10)

    if not isinstance(platforms, list) or not platforms:
        raise ValueError("At least one platform is required.")

    if not all(
        isinstance(platform, str)
        and platform in PLATFORM_ADAPTERS
        for platform in platforms
    ):
        raise ValueError("Unsupported platform selected.")

    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise ValueError("Maximum results must be an integer.")

    if not 1 <= max_results <= 100:
        raise ValueError("Maximum results must be between 1 and 100.")

    prospect_type = query_data.get("prospect_type", "")
    industry = query_data.get("industry") or ""
    location = query_data.get("location") or ""
    keywords = query_data.get("keywords", [])

    if not isinstance(prospect_type, str):
        raise ValueError("Prospect type must be a string.")

    if not isinstance(industry, str) or not isinstance(location, str):
        raise ValueError("Industry and location must be strings.")

    if not isinstance(keywords, list) or not all(
        isinstance(keyword, str) for keyword in keywords
    ):
        raise ValueError("Keywords must be a list of strings.")

    search_terms = [
        prospect_type,
        industry,
        location,
        *keywords,
    ]

    base_query = " ".join(
        term.strip()
        for term in search_terms
        if term.strip()
    )

    if not base_query:
        raise ValueError("Search requirements cannot be empty.")

    all_profiles = []
    successful_searches = 0
    search_errors = []

    for platform in platforms:
        adapter = PLATFORM_ADAPTERS[platform]

        try:
            search_query = adapter.build_search_query(base_query)

            results = search_web(
                search_query,
                max_results=min(max_results, 20),
            )

            successful_searches += 1

            profiles = extract_profiles(results)
            all_profiles.extend(profiles)

        except SearchServiceError:
            search_errors.append(
                f"Search failed for platform: {platform}"
            )

    if successful_searches == 0:
        raise SearchServiceError(
            "No platform searches completed successfully."
        )

    unique_profiles = deduplicate_profiles(all_profiles)

    relevant_profiles = filter_relevant_profiles(
        unique_profiles,
        query_data,
        minimum_score=20,
    )

    final_profiles = relevant_profiles[:max_results]

    return {
        "query": query_data,
        "total_discovered": len(all_profiles),
        "total_unique": len(unique_profiles),
        "total_relevant": len(relevant_profiles),
        "returned_count": len(final_profiles),
        "profiles": final_profiles,
        "search_errors": search_errors,
    }
