
import re
from urllib.parse import urlparse


PLATFORM_DOMAINS = {
    "linkedin.com": "linkedin",
    "x.com": "x",
    "twitter.com": "x",
    "youtube.com": "youtube",
    "instagram.com": "instagram",
    "facebook.com": "facebook",
    "threads.net": "threads",
    "wa.me": "whatsapp",
    "whatsapp.com": "whatsapp",
}

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "test.com",
    "invalid",
}


def identify_platform(url: str) -> str:
    """Identify the source platform from a public URL."""

    if not isinstance(url, str):
        return "unknown"

    try:
        parsed_url = urlparse(url)

        if parsed_url.scheme not in ("http", "https"):
            return "unknown"

        hostname = parsed_url.hostname or ""
        hostname = hostname.lower().removeprefix("www.")

        if not hostname:
            return "unknown"

        for domain, platform in PLATFORM_DOMAINS.items():
            if hostname == domain or hostname.endswith("." + domain):
                return platform

        return "google"

    except (ValueError, TypeError):
        return "unknown"


def extract_labeled_value(text: str, label: str):
    """Extract a value following an explicit text label."""

    pattern = rf"(?im)^\s*{re.escape(label)}:\s*(.+?)\s*$"
    match = re.search(pattern, text)

    return match.group(1).strip() if match else None


def is_valid_email_format(email: str) -> bool:
    """Check basic email syntax without claiming deliverability."""

    if not isinstance(email, str):
        return False

    email = email.strip()

    if not EMAIL_PATTERN.fullmatch(email):
        return False

    if len(email) > 254:
        return False

    local_part, domain = email.rsplit("@", 1)

    if len(local_part) > 64 or not local_part:
        return False

    if local_part.startswith(".") or local_part.endswith("."):
        return False

    if ".." in local_part or ".." in domain:
        return False

    if domain.lower() in PLACEHOLDER_DOMAINS:
        return False

    domain_labels = domain.split(".")

    if any(
        not label
        or label.startswith("-")
        or label.endswith("-")
        for label in domain_labels
    ):
        return False

    return True


def extract_public_email(text: str):
    """Extract the first syntactically valid email from public source text."""

    if not isinstance(text, str):
        return None

    for candidate in EMAIL_PATTERN.findall(text):
        candidate = candidate.strip()

        if is_valid_email_format(candidate):
            return candidate

    return None


def extract_profiles(search_results: list) -> list:
    """Extract structured information from public search results."""

    if not isinstance(search_results, list):
        raise ValueError("Search results must be a list.")

    profiles = []

    for item in search_results:
        if not isinstance(item, dict):
            continue

        url = item.get("url", "")

        if not isinstance(url, str):
            continue

        try:
            parsed_url = urlparse(url)

            if (
                parsed_url.scheme not in ("http", "https")
                or not parsed_url.hostname
            ):
                continue

        except ValueError:
            continue

        title = item.get("title", "")
        content = item.get("content", "")

        if not isinstance(title, str):
            title = ""

        if not isinstance(content, str):
            content = ""

        name = None

        heading = re.search(
            r"(?m)^\s*#\s+(.+?)\s*$",
            content,
        )

        if heading:
            name = heading.group(1).strip()

        if not name:
            name = extract_labeled_value(content, "Name")

        if not name:
            name = extract_labeled_value(content, "Full name")

        headline = extract_labeled_value(content, "Headline")
        current_role = extract_labeled_value(content, "Current role")
        location = extract_labeled_value(content, "Location")

        company = None

        if headline and "@" in headline:
            company = headline.rsplit("@", 1)[1].strip()

        contact_email = extract_public_email(content)

        profiles.append({
            "name": name,
            "title": current_role or headline or title,
            "company": company,
            "location": location,
            "profile_url": url,
            "contact_email": contact_email,
            "platform": identify_platform(url),
            "source_url": url,
            "source_text": content,
        })

    return profiles
