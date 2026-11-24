
from fastapi.testclient import TestClient

from app import main
from app.services.llm_service import LLMServiceError
from app.services.search_service import SearchServiceError


client = TestClient(main.app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_prospect_discovery_success(monkeypatch):
    def mock_understand_query(user_query):
        return {
            "prospect_type": "founders",
            "location": "Bengaluru",
            "industry": "SaaS",
            "keywords": ["cloud computing"],
            "max_results": 5,
            "platforms": ["google", "linkedin"],
        }

    def mock_discover_prospects(query_data):
        return {
            "query": query_data,
            "total_discovered": 2,
            "total_unique": 2,
            "total_relevant": 1,
            "returned_count": 1,
            "profiles": [
                {
                    "name": "Person A",
                    "title": "Founder and CEO",
                    "company": "CloudTech",
                    "location": "Bengaluru",
                    "profile_url": "https://linkedin.com/in/person-a",
                    "contact_email": None,
                    "platform": "linkedin",
                    "source_url": "https://linkedin.com/in/person-a",
                    "relevance_score": 80,
                }
            ],
            "search_errors": [],
        }

    monkeypatch.setattr(
        main,
        "understand_query",
        mock_understand_query,
    )

    monkeypatch.setattr(
        main,
        "discover_prospects",
        mock_discover_prospects,
    )

    response = client.post(
        "/prospect-discovery",
        json={"user_query": "Find SaaS founders in Bengaluru"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["returned_count"] == 1
    assert data["profiles"][0]["name"] == "Person A"


def test_empty_query_rejected_by_api():
    response = client.post(
        "/prospect-discovery",
        json={"user_query": ""},
    )

    assert response.status_code == 422


def test_missing_query_rejected_by_api():
    response = client.post(
        "/prospect-discovery",
        json={},
    )

    assert response.status_code == 422


def test_llm_service_failure(monkeypatch):
    def mock_understand_query(user_query):
        raise LLMServiceError("Internal Gemini error")

    monkeypatch.setattr(
        main,
        "understand_query",
        mock_understand_query,
    )

    response = client.post(
        "/prospect-discovery",
        json={"user_query": "Find SaaS founders"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The query understanding service is unavailable."
    )


def test_search_service_failure(monkeypatch):
    def mock_understand_query(user_query):
        return {
            "prospect_type": "founders",
            "location": "Bengaluru",
            "industry": "SaaS",
            "keywords": [],
            "max_results": 5,
            "platforms": ["google"],
        }

    def mock_discover_prospects(query_data):
        raise SearchServiceError("Internal search error")

    monkeypatch.setattr(
        main,
        "understand_query",
        mock_understand_query,
    )

    monkeypatch.setattr(
        main,
        "discover_prospects",
        mock_discover_prospects,
    )

    response = client.post(
        "/prospect-discovery",
        json={"user_query": "Find SaaS founders"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The prospect search service is unavailable."
    )


def test_unexpected_error_handled_safely(monkeypatch):
    def mock_understand_query(user_query):
        raise RuntimeError("Sensitive internal error")

    monkeypatch.setattr(
        main,
        "understand_query",
        mock_understand_query,
    )

    response = client.post(
        "/prospect-discovery",
        json={"user_query": "Find SaaS founders"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "An internal server error occurred."
    )

    assert "Sensitive internal error" not in response.text
