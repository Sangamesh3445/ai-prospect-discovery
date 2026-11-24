
from typing import Optional

from pydantic import BaseModel, Field


class ProspectDiscoveryRequest(BaseModel):
    user_query: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural-language prospect discovery request",
    )


class QueryDetails(BaseModel):
    prospect_type: str
    location: Optional[str] = None
    industry: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    max_results: int = Field(ge=1, le=100)
    platforms: list[str] = Field(default_factory=list)


class ProspectProfile(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    profile_url: str
    contact_email: Optional[str] = None
    platform: str
    source_url: str
    relevance_score: int = Field(ge=0, le=100)


class ProspectDiscoveryResponse(BaseModel):
    status: str
    query: QueryDetails
    total_discovered: int
    total_unique: int
    total_relevant: int
    returned_count: int
    profiles: list[ProspectProfile]
    search_errors: list[str] = Field(default_factory=list)
