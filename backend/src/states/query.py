"""Query-related state definitions."""

from typing import List

from pydantic import BaseModel, Field


class Query(BaseModel):
    """Individual query with rationale."""
    
    query: str = Field(
        description="The search query string"
    )
    rationale: str = Field(
        description="Explanation of why this query is relevant"
    )


class QueryGenerationState(BaseModel):
    """State for query generation phase."""
    
    search_query: List[str] = Field(
        default_factory=list,
        description="List of generated search queries"
    )