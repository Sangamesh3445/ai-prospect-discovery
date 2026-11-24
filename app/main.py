
import logging

from fastapi import FastAPI, HTTPException

from app.schemas import (
    ProspectDiscoveryRequest,
    ProspectDiscoveryResponse,
)
from app.services.query_service import understand_query
from app.services.llm_service import LLMServiceError
from app.services.search_service import SearchServiceError
from app.services.prospect_service import discover_prospects


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI-Powered Multi-Platform Prospect Discovery API",
    description=(
        "Discover and rank publicly available prospects "
        "using natural-language queries."
    ),
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Prospect Discovery API is running.",
        "docs": "/docs",
        "endpoint": "/prospect-discovery",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/prospect-discovery",
    response_model=ProspectDiscoveryResponse,
)
def prospect_discovery(
    request: ProspectDiscoveryRequest,
):
    try:
        query_data = understand_query(request.user_query)

        discovery_result = discover_prospects(query_data)

        return {
            "status": "success",
            **discovery_result,
        }

    except LLMServiceError:
        logger.exception("Query understanding service failed.")

        raise HTTPException(
            status_code=502,
            detail="The query understanding service is unavailable.",
        )

    except SearchServiceError:
        logger.exception("Prospect search service failed.")

        raise HTTPException(
            status_code=503,
            detail="The prospect search service is unavailable.",
        )

    except ValueError:
        logger.warning("Invalid prospect discovery request.")

        raise HTTPException(
            status_code=422,
            detail="The query could not be processed.",
        )

    except Exception:
        logger.exception("Unexpected error during prospect discovery.")

        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred.",
        )
