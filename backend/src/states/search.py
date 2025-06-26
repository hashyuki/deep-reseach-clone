"""Search-related state definitions."""

from pydantic import BaseModel, Field


class WebSearchState(BaseModel):
    """State for web search operations."""
    
    search_query: str = Field(
        description="The search query to execute"
    )
    id: int = Field(
        description="Unique identifier for this search operation"
    )


class SearchStateOutput(BaseModel):
    """Output state for search operations."""
    
    running_summary: str = Field(
        default="",
        description="Final research report summary"
    )