import json
import pytest

from app.services import query_service


SAMPLE_QUERIES = [
    (
        "Find 5 SaaS founders in Bengaluru interested in cloud computing",
        {
            "prospect_type": "SaaS founders",
            "location": "Bengaluru",
            "industry": "SaaS",
            "keywords": ["cloud computing"],
            "max_results": 5,
            "platforms": ["google", "linkedin"],
        },
    ),
    (
        "Find 10 marketing managers in Mumbai working in fintech",
        {
            "prospect_type": "marketing managers",
            "location": "Mumbai",
            "industry": "fintech",
            "keywords": ["marketing"],
            "max_results": 10,
            "platforms": ["google", "linkedin"],
        },
    ),
    (
        "Find 15 startup founders in Hyderabad using Instagram and X",
        {
            "prospect_type": "startup founders",
            "location": "Hyderabad",
            "industry": "startups",
            "keywords": [],
            "max_results": 15,
            "platforms": ["instagram", "x"],
        },
    ),
    (
        "Find 8 IT service companies in Chennai with public WhatsApp contacts",
        {
            "prospect_type": "IT service companies",
            "location": "Chennai",
            "industry": "IT services",
            "keywords": ["public WhatsApp contacts"],
            "max_results": 8,
            "platforms": ["google", "whatsapp"],
        },
    ),
    (
        "Find 20 HR professionals in Pune with publicly listed email addresses",
        {
            "prospect_type": "HR professionals",
            "location": "Pune",
            "industry": None,
            "keywords": ["publicly listed email addresses"],
            "max_results": 20,
            "platforms": ["google", "email"],
        },
    ),
]


@pytest.mark.parametrize(
    "user_query, expected",
    SAMPLE_QUERIES,
)
def test_sample_natural_language_queries(
    monkeypatch,
    user_query,
    expected,
):
    mock_response = json.dumps(expected)

    monkeypatch.setattr(
        query_service,
        "generate_response",
        lambda prompt: mock_response,
    )

    result = query_service.understand_query(user_query)

    assert result == expected


def test_sample_queries_are_sent_to_llm(monkeypatch):
    captured_prompts = []

    def mock_generate_response(prompt):
        captured_prompts.append(prompt)
        return json.dumps({
            "prospect_type": "founders",
            "location": "Bengaluru",
            "industry": "SaaS",
            "keywords": ["cloud computing"],
            "max_results": 5,
            "platforms": ["google", "linkedin"],
        })

    monkeypatch.setattr(
        query_service,
        "generate_response",
        mock_generate_response,
    )

    query_service.understand_query(
        "Find 5 SaaS founders in Bengaluru"
    )

    assert len(captured_prompts) == 1
    assert "Find 5 SaaS founders in Bengaluru" in captured_prompts[0]


def test_unsupported_platform_from_llm_rejected(monkeypatch):
    monkeypatch.setattr(
        query_service,
        "generate_response",
        lambda prompt: json.dumps({
            "prospect_type": "founders",
            "location": "Bengaluru",
            "industry": "SaaS",
            "keywords": [],
            "max_results": 5,
            "platforms": ["unsupported_platform"],
        }),
    )

    with pytest.raises(ValueError, match="Unsupported platform"):
        query_service.understand_query("Find SaaS founders")


def test_invalid_result_limit_from_llm_rejected(monkeypatch):
    monkeypatch.setattr(
        query_service,
        "generate_response",
        lambda prompt: json.dumps({
            "prospect_type": "founders",
            "location": "Bengaluru",
            "industry": "SaaS",
            "keywords": [],
            "max_results": 500,
            "platforms": ["google"],
        }),
    )

    with pytest.raises(ValueError, match="Maximum results"):
        query_service.understand_query("Find SaaS founders")
