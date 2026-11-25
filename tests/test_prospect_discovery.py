
import pytest

from app.services.query_service import (
    parse_json_response,
    understand_query,
)
from app.services.profile_extractor import (
    extract_profiles,
    is_valid_email_format,
    extract_public_email,
)
from app.services.deduplication_service import deduplicate_profiles
from app.services.relevance_service import filter_relevant_profiles


def test_parse_valid_json_response():
    response = '{"prospect_type": "founders"}'

    result = parse_json_response(response)

    assert result["prospect_type"] == "founders"


def test_parse_json_with_markdown():
    response = '```json\n{"prospect_type": "founders"}\n```'

    result = parse_json_response(response)

    assert result["prospect_type"] == "founders"


def test_parse_invalid_json():
    with pytest.raises(ValueError):
        parse_json_response("This is not JSON")


def test_empty_query_rejected():
    with pytest.raises(ValueError):
        understand_query("   ")


def test_extract_public_profile():
    results = [
        {
            "title": "LinkedIn Profile",
            "url": "https://linkedin.com/in/person-a",
            "content": (
                "Name: Person A\n"
                "Current role: Founder and CEO\n"
                "Location: Bengaluru"
            ),
        }
    ]

    profiles = extract_profiles(results)

    assert len(profiles) == 1
    assert profiles[0]["name"] == "Person A"
    assert profiles[0]["title"] == "Founder and CEO"
    assert profiles[0]["location"] == "Bengaluru"
    assert profiles[0]["platform"] == "linkedin"


def test_invalid_profile_url_rejected():
    results = [
        {
            "title": "Invalid profile",
            "url": "javascript:alert(1)",
            "content": "Name: Person A",
        }
    ]

    profiles = extract_profiles(results)

    assert profiles == []


def test_duplicate_profiles_removed():
    profiles = [
        {
            "name": "Person A",
            "profile_url": "https://linkedin.com/in/person-a/",
        },
        {
            "name": "Person A",
            "profile_url": "https://linkedin.com/in/person-a",
        },
        {
            "name": "Person B",
            "profile_url": "https://linkedin.com/in/person-b",
        },
    ]

    unique = deduplicate_profiles(profiles)

    assert len(unique) == 2


def test_founder_relevance_filter():
    query = {
        "prospect_type": "founders",
        "industry": "SaaS",
        "location": "Bengaluru",
        "keywords": ["cloud computing"],
    }

    profiles = [
        {
            "name": "Person A",
            "title": "Founder and CEO at CloudTech",
            "company": "CloudTech",
            "location": "Bengaluru",
            "profile_url": "https://linkedin.com/in/person-a",
            "source_text": "Current role: Founder and CEO",
        },
        {
            "name": "Person B",
            "title": "Senior Software Engineer",
            "company": "TechCorp",
            "location": "Bengaluru",
            "profile_url": "https://linkedin.com/in/person-b",
            "source_text": "Current role: Senior Software Engineer",
        },
    ]

    relevant = filter_relevant_profiles(
        profiles,
        query,
        minimum_score=20,
    )

    assert len(relevant) == 1
    assert relevant[0]["name"] == "Person A"


def test_directory_page_rejected():
    query = {
        "prospect_type": "founders",
        "industry": "SaaS",
        "location": "Bengaluru",
        "keywords": [],
    }

    profiles = [
        {
            "name": None,
            "title": "Founder Index: Indian Startup Founders",
            "profile_url": "https://example.com/founders",
            "source_text": "Founder Index directory",
        }
    ]

    relevant = filter_relevant_profiles(
        profiles,
        query,
        minimum_score=20,
    )

    assert relevant == []


# Email validation tests

def test_valid_email_format():
    assert is_valid_email_format("contact@cloudtech.io") is True


def test_invalid_email_format():
    assert is_valid_email_format("contact@invalid") is False


def test_placeholder_email_rejected():
    assert is_valid_email_format("person@example.com") is False


def test_public_email_extraction():
    text = (
        "Contact: invalid-address\n"
        "Email: contact@cloudtech.io"
    )

    assert extract_public_email(text) == "contact@cloudtech.io"


def test_no_public_email_returns_none():
    text = "Founder of a SaaS company in Bengaluru."

    assert extract_public_email(text) is None
# WhatsApp platform identification tests

def test_whatsapp_link_identification():
    from app.services.profile_extractor import identify_platform

    assert identify_platform(
        "https://wa.me/919876543210"
    ) == "whatsapp"


def test_whatsapp_api_identification():
    from app.services.profile_extractor import identify_platform

    assert identify_platform(
        "https://api.whatsapp.com/send"
    ) == "whatsapp"


def test_linkedin_platform_identification():
    from app.services.profile_extractor import identify_platform

    assert identify_platform(
        "https://linkedin.com/in/person-a"
    ) == "linkedin"

# Generic website and Google domain identification tests

def test_generic_website_identified_as_web():
    from app.services.profile_extractor import identify_platform

    assert identify_platform(
        "https://cloudtech.io/about"
    ) == "web"


def test_google_domain_identification():
    from app.services.profile_extractor import identify_platform

    assert identify_platform(
        "https://www.google.com/search"
    ) == "google"


def test_google_india_domain_identification():
    from app.services.profile_extractor import identify_platform

    assert identify_platform(
        "https://www.google.co.in/search"
    ) == "google"


def test_invalid_platform_url_identification():
    from app.services.profile_extractor import identify_platform

    assert identify_platform("javascript:alert(1)") == "unknown"
