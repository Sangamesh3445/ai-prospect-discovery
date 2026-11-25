
@'
# AI-Powered Multi-Platform Prospect Discovery API

A Python 3.12 and FastAPI application that converts natural-language prospect searches into structured requirements, discovers publicly indexed information through Tavily, extracts profile details, removes duplicates, and ranks relevant prospects.

## 1. Features

- Natural-language query understanding using Google Gemini.
- Multi-platform search-query generation.
- Public web discovery through Tavily Search API.
- Profile and publicly published email extraction.
- Email syntax validation.
- Duplicate profile removal.
- Rule-based relevance scoring and filtering.
- Structured JSON responses using Pydantic.
- FastAPI validation and error handling.
- Automated unit, API, and pipeline tests.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI |
| LLM | Google Gemini API |
| Search provider | Tavily Search API |
| Data validation | Pydantic |
| HTTP client | HTTPX |
| Testing | pytest |

## 3. Architecture and Workflow

1. The client submits a natural-language query to `POST /prospect-discovery`.
2. Gemini extracts prospect type, location, industry, keywords, result limit, and requested platforms.
3. Platform adapters construct targeted search queries.
4. Tavily searches publicly indexed web content.
5. The profile extractor identifies available names, titles, companies, locations, profile URLs, and public email addresses.
6. Email syntax validation rejects malformed and placeholder addresses.
7. Deduplication removes repeated profile/source URLs.
8. The relevance service scores and filters discovered profiles.
9. FastAPI returns a structured JSON response.

## 4. Supported Discovery Targets

| Target | Discovery approach |
|---|---|
| Google | General web search |
| LinkedIn | LinkedIn-focused site queries |
| X | X-focused site queries |
| YouTube | YouTube-focused site queries |
| Instagram | Instagram-focused site queries |
| Facebook | Facebook-focused site queries |
| Threads | Threads-focused site queries |
| WhatsApp | Publicly indexed WhatsApp Business links |
| Email | Publicly indexed contact and email searches |

**Implementation note:** These are search-query adapters routed through Tavily, not nine independent official platform API integrations. Results depend on public indexing and provider availability. Private accounts, restricted content, and non-public contact information are not accessed.

## 5. Installation

Clone the repository:

```bash
git clone https://github.com/Sangamesh3445/ai-prospect-discovery.git
cd ai-prospect-discovery
```

Create a virtual environment using Python 3.12:

```powershell
py -3.12 -m venv venv
```

Install dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Configure the required Gemini and Tavily API credentials in `.env`. Never commit this file.

## 6. Run the API

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

Interactive API documentation: `http://127.0.0.1:8000/docs`

Health endpoint: `GET /health`

Main endpoint: `POST /prospect-discovery`

## 7. Sample Request

```json
{
  "user_query": "Find 5 SaaS founders in Bengaluru interested in cloud computing"
}
```

Send the request to:

```text
POST http://127.0.0.1:8000/prospect-discovery
```

The API returns structured JSON containing query details, discovery counts, prospect profiles, and any search errors.

## 8. Run Tests

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

The current automated test suite contains 27 tests covering API behavior, query processing, prospect discovery, and pipeline operations.

## 9. Limitations and Responsible Use

- Discovery is limited to publicly indexed information.
- Search results may be incomplete or unavailable.
- Email validation checks syntax, not mailbox existence or deliverability.
- Relevance scores are rule-based estimates, not guarantees.
- Users should independently verify prospect identity and contact details.
- The application does not bypass authentication or access private data.

## 10. Security

- Store API credentials in `.env`.
- `.env` and the virtual environment are excluded through `.gitignore`.
- Use `.env.example` as the configuration template.
- Do not publish API keys, tokens, or private prospect information.

## 11. Deployment

The application can be served using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure the required environment variables in the deployment provider.

## 12. Repository

GitHub: https://github.com/Sangamesh3445/ai-prospect-discovery

## License

Developed as a technical assessment project.
'@ | Set-Content -Path README.md -Encoding utf8
