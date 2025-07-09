from langgraph.graph import END, START, StateGraph
from src.nodes import (
    FinalizationNode,
    QueryGenerationNode,
    ReflectionNode,
    WebResearchNode,
)
from src.routers import ResearchEvaluationRouter, WebResearchRouter
from src.states import OverallState


# Create router instances
web_research_router = WebResearchRouter()
research_evaluation_router = ResearchEvaluationRouter()

# Create our Research Agent Graph
builder = StateGraph(OverallState)

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

# Compile the graph with better metadata
research_graph = builder.compile(
    checkpointer=None  # Using in-memory checkpointing for development
)
