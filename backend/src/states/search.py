from pydantic import BaseModel, Field


class WebSearchState(BaseModel):
    """ウェブ検索クエリを格納するState"""

    id: int = Field(description="この検索操作の一意識別子")
    search_query: str = Field(description="実行する検索クエリ")
