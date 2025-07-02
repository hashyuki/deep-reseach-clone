from typing import List, Union

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage


def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    メッセージから研究トピックを取得します。
    """

    def content_to_str(content: Union[str, list]) -> str:
        """メッセージ内容を文字列に変換します。"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # コンテンツブロックのリストを処理
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

    # リクエストに履歴があるかチェックし、メッセージを1つの文字列に結合
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
