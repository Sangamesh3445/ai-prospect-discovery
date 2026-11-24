# AI-Powered Multi-Platform Prospect Discovery API

A FastAPI application that uses Google Gemini to understand natural-language prospect searches and Tavily to discover publicly indexed prospect information.

## Features

- Natural-language query processing using Gemini.
- Public web search using Tavily.
- Search-query adapters for nine target platforms.
- Profile and publicly available email extraction.
- Email syntax validation.
- Duplicate removal and relevance scoring.
- Structured JSON API responses.
- Automated tests using pytest.

## Tech Stack

Python 3.12 | FastAPI | Gemini API | Tavily API | Pydantic | pytest

## Installation

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file using `.env.example` and configure:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash
TAVILY_API_KEY=your_tavily_api_key
```

## Run the Application

```bash
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

Main endpoint: `POST /prospect-discovery`

Example request:

```json
{
  "user_query": "Find 5 SaaS founders in Bengaluru interested in cloud computing"
}
```

## Run Tests

```bash
pytest -v
```

## Implementation Notes

Platform modules construct targeted search queries executed through Tavily; they are not independent official platform API integrations.

The application targets publicly indexed information. Email validation checks syntax, not deliverability. Extracted information and relevance scores should be independently verified.

API credentials must remain in `.env`, which is excluded from Git.

## License

Developed as a technical assessment project.