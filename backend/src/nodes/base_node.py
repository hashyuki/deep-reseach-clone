from abc import ABC, abstractmethod
from typing import List, Union

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send
from pydantic import BaseModel


class BaseNode(ABC):
    """
    LangGraphノードの基底クラス
    """

    @abstractmethod
    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """ノードロジックを実行

        Args:
            state: 現在のグラフ状態
            config: 実行可能な設定

        Returns:
            更新されたグラフ状態、Sendオブジェクトのリスト、または文字列
        """
        pass
