"""Reflection state definitions."""

import operator
from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class ReflectionState(BaseModel):
    """State for reflection phase of research."""

    is_sufficient: bool = Field(
        description="Whether the current research is sufficient to answer the question"
    )
    knowledge_gap: str = Field(
        description="Description of what information is missing or needs clarification"
    )
    follow_up_queries: Annotated[List[str], operator.add] = Field(
        default_factory=list,
        description="List of follow-up queries to address knowledge gaps"
    )
    research_loop_count: int = Field(
        default=0,
        description="Current number of research loops performed"
    )
    number_of_ran_queries: int = Field(
        default=0,
        description="Total number of queries that have been executed"
    )
    max_research_loops: Optional[int] = Field(
        default=None,
        description="Maximum number of research loops to perform"
    )

    class Config:
        arbitrary_types_allowed = True