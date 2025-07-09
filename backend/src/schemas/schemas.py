from typing import List

from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    """検索クエリ生成出力用のスキーマ"""

    query: List[str] = Field(description="ウェブ研究に使用される検索クエリのリスト")
    rationale: str = Field(
        description="これらのクエリが研究トピックに関連する理由の簡潔な説明"
    )


class Reflection(BaseModel):
    """リフレクション分析出力用のスキーマ"""

    is_sufficient: bool = Field(
        description="提供された要約がユーザーの質問に答えるのに十分かどうか"
    )
    knowledge_gap: str = Field(description="不足している情報や明確化が必要な情報の説明")
    follow_up_queries: List[str] = Field(
        description="知識のギャップに対処するためのフォローアップクエリのリスト"
    )
