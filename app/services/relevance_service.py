
import re


FOUNDER_TERMS = [
    "founder",
    "co-founder",
    "cofounder",
    "chief executive officer",
    "ceo",
]

NON_PERSON_PAGE_TERMS = [
    "directory",
    "index",
    "job listing",
    "jobs",
    "hiring",
    "investors",
    "startup list",
    "startups in",
    "founder index",
    "founders",
    "list of founders",
]


def has_founder_evidence(profile: dict) -> bool:
    """Require evidence that a prospect actually has a founder role."""

    title = str(profile.get("title") or "").lower()
    source = str(profile.get("source_text") or "").lower()

    # Check the title or an explicitly labelled professional role.
    if any(term in title for term in FOUNDER_TERMS):
        return True

    role_lines = re.findall(
        r"(?im)^\s*(?:current role|headline)\s*:\s*(.+)$",
        source,
    )

    return any(
        any(term in line.lower() for term in FOUNDER_TERMS)
        for line in role_lines
    )


def is_directory_or_job_page(profile: dict) -> bool:
    """Identify obvious directory and recruitment pages."""

    title = str(profile.get("title") or "").lower()
    url = str(profile.get("profile_url") or "").lower()

    return any(
        term in title or term in url
        for term in NON_PERSON_PAGE_TERMS
    )


def calculate_relevance(profile: dict, query_data: dict) -> int:
    """Calculate a relevance score from 0 to 100."""

    if not isinstance(profile, dict) or not isinstance(query_data, dict):
        raise ValueError("Profile and query data must be dictionaries.")

    searchable_text = " ".join(
        str(profile.get(field) or "")
        for field in [
            "name",
            "title",
            "company",
            "location",
            "source_text",
        ]
    ).lower()

    score = 0

    keywords = query_data.get("keywords", [])

    if not isinstance(keywords, list):
        raise ValueError("Keywords must be a list.")

    for keyword in keywords:
        if isinstance(keyword, str) and keyword.strip():
            if keyword.lower() in searchable_text:
                score += 15

    industry = query_data.get("industry")
    if isinstance(industry, str) and industry.strip():
        if industry.lower() in searchable_text:
            score += 15

    location = query_data.get("location")
    if isinstance(location, str) and location.strip():
        if location.lower() in searchable_text:
            score += 15

    prospect_type = query_data.get("prospect_type", "")

    if isinstance(prospect_type, str) and prospect_type.strip():
        if prospect_type.lower() in searchable_text:
            score += 15

    if profile.get("name"):
        score += 10

    if profile.get("company"):
        score += 10

    if profile.get("profile_url"):
        score += 20

    # Founder searches require explicit role evidence.
    if "founder" in str(prospect_type).lower():
        if not has_founder_evidence(profile):
            return 0

    # Do not recommend obvious directory or job-listing pages.
    if is_directory_or_job_page(profile):
        return 0

    return min(score, 100)


def filter_relevant_profiles(
    profiles: list,
    query_data: dict,
    minimum_score: int = 20,
) -> list:
    """Filter prospects and rank them by relevance."""

    if not isinstance(profiles, list):
        raise ValueError("Profiles must be a list.")

    if isinstance(minimum_score, bool) or not isinstance(minimum_score, int):
        raise ValueError("Minimum score must be an integer.")

    if not 0 <= minimum_score <= 100:
        raise ValueError("Minimum score must be between 0 and 100.")

    relevant_profiles = []

    for profile in profiles:
        score = calculate_relevance(profile, query_data)

        if score >= minimum_score:
            enriched_profile = profile.copy()
            enriched_profile["relevance_score"] = score
            relevant_profiles.append(enriched_profile)

    return sorted(
        relevant_profiles,
        key=lambda item: item["relevance_score"],
        reverse=True,
    )
