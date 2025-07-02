"""Base state definitions for the agent."""

from __future__ import annotations

import operator
from typing import List, Optional, Any

from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class OverallState(BaseModel):
    """Overall state for the research agent."""
    
    messages: Annotated[List[Any], add_messages] = Field(
        default_factory=list,
        description="List of messages in the conversation"
    )
    search_query: Annotated[List[str], operator.add] = Field(
        default_factory=list,
        description="List of search queries generated and executed"
    )
    web_research_result: Annotated[List[str], operator.add] = Field(
        default_factory=list,
        description="List of web research results"
    )
    sources_gathered: Annotated[List[dict], operator.add] = Field(
        default_factory=list,
        description="List of sources gathered during research"
    )
    initial_search_query_count: Annotated[Optional[int], lambda x, y: y or x] = Field(
        default=None,
        description="Number of initial search queries to generate"
    )
    max_research_loops: Annotated[Optional[int], lambda x, y: y or x] = Field(
        default=None,
        description="Maximum number of research loops to perform"
    )
    research_loop_count: Annotated[int, lambda x, y: y if y > x else x] = Field(
        default=0,
        description="Current number of research loops performed"
    )
    reasoning_model: Annotated[Optional[str], lambda x, y: y or x] = Field(
        default=None,
        description="Model to use for reasoning tasks"
    )

    class Config:
        arbitrary_types_allowed = True