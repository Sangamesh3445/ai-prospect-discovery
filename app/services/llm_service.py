
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


class LLMServiceError(Exception):
    """Raised when the LLM service cannot process a request."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def generate_response(prompt: str) -> str:
    """Generate a response using the configured Gemini model."""

    if not API_KEY:
        raise LLMServiceError(
            "Gemini API key is not configured.",
            status_code=503,
        )

    client = None

    try:
        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        if not response.text:
            raise LLMServiceError(
                "Gemini returned an empty response.",
                status_code=503,
            )

        return response.text.strip()

    except LLMServiceError:
        raise

    except Exception as exc:
        error_code = (
            getattr(exc, "code", None)
            or getattr(exc, "status_code", None)
        )

        try:
            error_code = int(error_code)
        except (TypeError, ValueError):
            error_code = 503

        if error_code == 429:
            raise LLMServiceError(
                "Gemini API quota exceeded. Please retry after the quota resets.",
                status_code=429,
            ) from exc

        raise LLMServiceError(
            "The language model request failed.",
            status_code=503,
        ) from exc

    finally:
        if client is not None:
            client.close()
