import operator
from typing import Optional, Any

from langgraph.graph import add_messages
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated


class OverallState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    messages: Annotated[list[Any], add_messages] = Field(
        default_factory=list, description="会話内のメッセージリスト"
    )
    search_query: Annotated[list[str], operator.add] = Field(
        default_factory=list, description="生成・実行された検索クエリのリスト"
    )
    web_research_result: Annotated[list[str], operator.add] = Field(
        default_factory=list, description="ウェブリサーチ結果のリスト"
    )
    sources_gathered: Annotated[list[dict], operator.add] = Field(
        default_factory=list, description="リサーチ中に収集されたソースのリスト"
    )
    initial_search_query_count: Annotated[Optional[int], lambda x, y: y or x] = Field(
        default=None, description="生成する初期検索クエリの数"
    )
    max_research_loops: Annotated[Optional[int], lambda x, y: y or x] = Field(
        default=None, description="実行する最大リサーチループ数"
    )
    research_loop_count: Annotated[int, lambda x, y: y if y > x else x] = Field(
        default=0, description="実行済みの現在のリサーチループ数"
    )
    reasoning_model: Annotated[Optional[str], lambda x, y: y or x] = Field(
        default=None, description="推論タスクに使用するモデル"
    )
