import pytest

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


@pytest.mark.parametrize(
    "adapter, expected",
    [
        (google, "SaaS founders Bengaluru"),
        (linkedin, "site:linkedin.com/in"),
        (x_platform, "site:x.com"),
        (youtube, "site:youtube.com"),
        (instagram, "site:instagram.com"),
        (facebook, "site:facebook.com"),
        (threads, "site:threads.net"),
        (whatsapp, "site:wa.me"),
        (email, '"email" OR "contact"'),
    ],
)
def test_platform_search_query(adapter, expected):
    result = adapter.build_search_query(
        "SaaS founders Bengaluru"
    )

    assert expected in result
    assert "SaaS founders Bengaluru" in result


@pytest.mark.parametrize(
    "adapter",
    [
        google,
        linkedin,
        x_platform,
        youtube,
        instagram,
        facebook,
        threads,
        whatsapp,
        email,
    ],
)
@pytest.mark.parametrize("query", ["", "   ", None])
def test_platform_adapters_reject_empty_queries(adapter, query):
    with pytest.raises(ValueError):
        adapter.build_search_query(query)


def test_whatsapp_query_includes_public_business_domains():
    result = whatsapp.build_search_query("SaaS founders")

    assert "wa.me" in result
    assert "api.whatsapp.com" in result
    assert "whatsapp.com" in result


def test_linkedin_query_targets_profile_pages():
    result = linkedin.build_search_query("cloud founders")

    assert "site:linkedin.com/in" in result


def test_email_query_targets_published_contact_information():
    result = email.build_search_query("SaaS companies")

    assert '"email"' in result
    assert '"contact"' in result
    assert '"contact us"' in result
