from typing import Hashable, List, Union, cast

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send
from src.routers.base_router import BaseRouter
from src.states import OverallState, WebSearchState


class WebResearchRouter(BaseRouter):
    """
    Web研究のルーティングを行うルーター
    """

    def _create_search_tasks(
        self, queries: List[str], state: OverallState
    ) -> List[Send]:
        """並列検索タスクを作成"""
        return [
            Send(
                "web_research",
                WebSearchState(
                    search_query=query,
                    id=len(state.search_query) + int(idx),
                ),
            )
            for idx, query in enumerate(queries)
        ]

    def __call__(
        self, state: OverallState, config: RunnableConfig
    ) -> Union[Hashable, List[Hashable]]:
        """Web研究へのルーティングを決定

        Args:
            state: 現在のグラフ状態
            config: 実行可能な設定

        Returns:
            次のノード名またはSendオブジェクトのリスト
        """
        # 検索クエリが存在する場合は並列検索タスクを作成
        if state.search_query:
            return cast(
                List[Hashable], self._create_search_tasks(state.search_query, state)
            )

        # 検索クエリが無い場合は終了
        return "finalize_answer"
