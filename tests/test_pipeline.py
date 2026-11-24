
from app.services import prospect_service
from app.services.search_service import SearchServiceError


QUERY = {
    "prospect_type": "founders",
    "location": "Bengaluru",
    "industry": "SaaS",
    "keywords": ["cloud computing"],
    "max_results": 5,
    "platforms": ["google", "linkedin", "whatsapp", "email"],
}


MOCK_RESULTS = [
    {
        "title": "Person A Founder and CEO",
        "url": "https://linkedin.com/in/person-a",
        "content": (
            "Name: Person A\n"
            "Current role: Founder and CEO\n"
            "Location: Bengaluru\n"
            "Industry: SaaS\n"
            "Keywords: cloud computing\n"
            "Email: contact@cloudtech.io"
        ),
    }
]


def test_discovery_pipeline_deduplicates_results(monkeypatch):
    search_calls = []

    def mock_search(query, max_results=10):
        search_calls.append(query)
        return MOCK_RESULTS

    monkeypatch.setattr(
        prospect_service,
        "search_web",
        mock_search,
    )

    result = prospect_service.discover_prospects(QUERY)

    assert len(search_calls) == 4
    assert result["total_discovered"] == 4
    assert result["total_unique"] == 1
    assert result["total_relevant"] == 1
    assert result["returned_count"] == 1
    assert result["search_errors"] == []


def test_discovery_pipeline_handles_partial_search_failure(monkeypatch):
    def mock_search(query, max_results=10):
        if query.startswith("site:linkedin.com/in"):
            raise SearchServiceError("Simulated search failure")

        return MOCK_RESULTS

    monkeypatch.setattr(
        prospect_service,
        "search_web",
        mock_search,
    )

    result = prospect_service.discover_prospects(QUERY)

    assert result["total_discovered"] == 3
    assert result["total_unique"] == 1
    assert result["returned_count"] == 1
    assert len(result["search_errors"]) == 1
    assert "linkedin" in result["search_errors"][0]
