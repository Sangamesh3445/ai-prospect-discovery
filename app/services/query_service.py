
import json

from app.services.llm_service import (
    generate_response,
    LLMServiceError,
)


ALLOWED_PLATFORMS = [
    "google",
    "linkedin",
    "x",
    "youtube",
    "instagram",
    "facebook",
    "threads",
    "whatsapp",
    "email",
]


def parse_json_response(response: str) -> dict:
    """Safely parse JSON returned by the language model."""

    if not isinstance(response, str) or not response.strip():
        raise ValueError("The language model returned an empty response.")

    cleaned_response = response.strip()

    if cleaned_response.startswith("```"):
        lines = cleaned_response.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned_response = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned_response)

    except json.JSONDecodeError:
        start = cleaned_response.find("{")
        end = cleaned_response.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "The language model did not return valid JSON."
            )

        try:
            data = json.loads(cleaned_response[start:end + 1])

        except json.JSONDecodeError as exc:
            raise ValueError(
                "The language model returned invalid JSON."
            ) from exc

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")

    return data


def understand_query(user_query: str) -> dict:
    """Convert a natural-language prospect query into structured data."""

    if not isinstance(user_query, str):
        raise ValueError("Query must be a string.")

    user_query = user_query.strip()

    if not user_query:
        raise ValueError("Query cannot be empty.")

    if len(user_query) > 2000:
        raise ValueError("Query is too long. Maximum 2000 characters.")

    prompt = f"""
You are a query understanding component for a prospect discovery API.

Extract the user's prospect search requirements.

Return ONLY one valid JSON object.
Do not use Markdown code fences.
Do not include explanations or additional text.

Use exactly these fields:
{{
    "prospect_type": "string",
    "location": null,
    "industry": null,
    "keywords": [],
    "max_results": 10,
    "platforms": ["google", "linkedin"]
}}

Rules:
- Never invent missing information.
- Use null when location or industry is unspecified.
- Default max_results to 10.
- Maximum max_results is 100.
- Only use platforms from this list:
{json.dumps(ALLOWED_PLATFORMS)}
- If no platform is specified, select google and linkedin.
- WhatsApp means publicly indexed WhatsApp Business links only.
- Email means publicly published contact email addresses only.
- Never invent or guess contact information.
- Return JSON only.

User query:
{json.dumps(user_query)}
"""

    try:
        response = generate_response(prompt)

        data = parse_json_response(response)

        prospect_type = data.get("prospect_type")

        if not isinstance(prospect_type, str) or not prospect_type.strip():
            raise ValueError("Invalid prospect type.")

        keywords = data.get("keywords", [])
        platforms = data.get("platforms", [])

        if not isinstance(keywords, list):
            raise ValueError("Invalid keywords.")

        if not isinstance(platforms, list):
            raise ValueError("Invalid platforms.")

        if not all(
            isinstance(item, str) and item.strip()
            for item in keywords
        ):
            raise ValueError("Keywords must contain non-empty strings.")

        if not all(
            isinstance(item, str) and item in ALLOWED_PLATFORMS
            for item in platforms
        ):
            raise ValueError("Unsupported platform returned.")

        if not platforms:
            raise ValueError("At least one platform is required.")

        max_results = data.get("max_results", 10)

        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("Invalid maximum results value.")

        if not 1 <= max_results <= 100:
            raise ValueError(
                "Maximum results must be between 1 and 100."
            )

        location = data.get("location")
        industry = data.get("industry")

        if location is not None and not isinstance(location, str):
            raise ValueError("Invalid location.")

        if industry is not None and not isinstance(industry, str):
            raise ValueError("Invalid industry.")

        return {
            "prospect_type": prospect_type.strip(),
            "location": location.strip() if location else None,
            "industry": industry.strip() if industry else None,
            "keywords": keywords,
            "max_results": max_results,
            "platforms": platforms,
        }

    except LLMServiceError:
        raise
