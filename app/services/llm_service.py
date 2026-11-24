
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


class LLMServiceError(Exception):
    """Raised when the LLM service cannot process a request."""


def generate_response(prompt: str) -> str:
    """Generate a response using the configured Gemini model."""

    if not API_KEY:
        raise LLMServiceError("Gemini API key is not configured.")

    client = None

    try:
        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if not response.text:
            raise LLMServiceError("Gemini returned an empty response.")

        return response.text.strip()

    except LLMServiceError:
        raise

    except Exception as exc:
        # Avoid exposing API credentials or internal error details.
        raise LLMServiceError(
            "The language model request failed."
        ) from exc

    finally:
        if client is not None:
            client.close()
