"""Message processing utilities."""

from typing import List, Union

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage


def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    
    def content_to_str(content: Union[str, list]) -> str:
        """Convert message content to string."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Handle list of content blocks
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    text_parts.append(str(item["text"]))
                else:
                    text_parts.append(str(item))
            return " ".join(text_parts)
        else:
            return str(content)
    
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = content_to_str(messages[-1].content)
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {content_to_str(message.content)}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {content_to_str(message.content)}\n"
    return research_topic
