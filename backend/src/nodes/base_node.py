from abc import ABC, abstractmethod
from typing import List, Union

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send
from pydantic import BaseModel


class BaseNode(ABC):
    """LangGraphノードの基底クラス。

    すべてのノードはこのクラスを継承し、統一されたインターフェースを提供します。
    各ノードは状態を受け取り、処理を実行し、更新された状態を返す必要があります。
    """

    def __init__(self):
        """ベースノードを初期化。"""
        pass

    @abstractmethod
    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """ノードロジックを実行。

        Args:
            state: 現在のグラフ状態
            config: 実行可能な設定

        Returns:
            更新されたグラフ状態、Sendオブジェクトのリスト、または文字列
        """
        pass
