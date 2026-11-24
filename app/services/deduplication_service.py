
def deduplicate_profiles(profiles: list) -> list:
    """Remove duplicate prospects using their profile or source URLs."""

    if not isinstance(profiles, list):
        raise ValueError("Profiles must be a list.")

    unique_profiles = []
    seen_urls = set()

    for profile in profiles:
        if not isinstance(profile, dict):
            continue

        url = profile.get("profile_url") or profile.get("source_url")

        if not isinstance(url, str) or not url.strip():
            continue

        normalized_url = url.strip().lower().rstrip("/")

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        unique_profiles.append(profile)

    return unique_profiles
