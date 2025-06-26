from typing import Hashable, Union, cast

from config import Configuration
from langgraph.graph import END, START, StateGraph
from nodes import (
    FinalizationNode,
    QueryGenerationNode,
    ReflectionNode,
    ResearchEvaluationNode,
    WebResearchNode,
    WebResearchRouterNode,
)
from states import OverallState


# Router functions for conditional edges
def web_research_router(state: OverallState) -> Union[Hashable, list[Hashable]]:
    """Route to web research based on search queries."""
    result = WebResearchRouterNode()(state, {})
    if isinstance(result, list):
        return cast(list[Hashable], result)  # Cast Send objects to Hashable
    return "web_research"


def research_evaluation_router(state: OverallState) -> Union[Hashable, list[Hashable]]:
    """Route based on research evaluation."""
    result = ResearchEvaluationNode()(state, {})
    if isinstance(result, str):
        return result
    elif isinstance(result, list):
        return cast(list[Hashable], result)  # Cast Send objects to Hashable
    return "finalize_answer"


# Create our Research Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", QueryGenerationNode())
builder.add_node("web_research", WebResearchNode())
builder.add_node("reflection", ReflectionNode())
builder.add_node("finalize_answer", FinalizationNode())

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges("generate_query", web_research_router, ["web_research"])
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", research_evaluation_router, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

research_graph = builder.compile(name="pro-search-agent")
