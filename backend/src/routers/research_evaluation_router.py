from typing import Hashable, List, Union, cast

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send
from src.config.configuration import Configuration
from src.routers.base_router import BaseRouter
from src.states import OverallState, WebSearchState


class ResearchEvaluationRouter(BaseRouter):
    """
    研究の進捗を評価し、次のステップを決定するルーター
    """

    def _get_max_research_loops(self, state: OverallState, config_obj) -> int:
        """状態または設定から最大研究ループ数を取得"""
        return (
            state.max_research_loops
            if state.max_research_loops is not None
            else config_obj.research.max_research_loops
        )

    def _should_finalize_research(self, state: OverallState, max_loops: int) -> bool:
        """研究を終了すべきかどうかを判断"""
        return state.research_loop_count >= max_loops

    def _create_follow_up_searches(self, state: OverallState, config_obj) -> List[Send]:
        """知識ギャップのフォローアップ検索タスクを作成"""
        max_follow_up = config_obj.research.max_follow_up_queries

        return [
            Send(
                "web_research",
                WebSearchState(
                    search_query=follow_up_query,
                    id=len(state.search_query) + int(idx),
                ),
            )
            for idx, follow_up_query in enumerate(state.search_query[-max_follow_up:])
        ]

    def __call__(
        self, state: OverallState, config: RunnableConfig
    ) -> Union[Hashable, List[Hashable]]:
        """研究フローの次のステップを決定

        Args:
            state: 現在のグラフ状態
            config: 実行可能な設定

        Returns:
            次のノード名またはSendオブジェクトのリスト
        """
        # 設定を取得
        config_obj = Configuration.get_config(config)
        max_research_loops = self._get_max_research_loops(state, config_obj)

        if self._should_finalize_research(state, max_research_loops):
            return "finalize_answer"
        else:
            return cast(
                List[Hashable], self._create_follow_up_searches(state, config_obj)
            )
