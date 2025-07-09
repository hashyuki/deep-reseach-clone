from abc import ABC, abstractmethod
from typing import Hashable, List, Union
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel


class BaseRouter(ABC):
    """
    ルーターの基底クラス
    """

    @abstractmethod
    def __call__(
        self, state: BaseModel, config: RunnableConfig
    ) -> Union[Hashable, List[Hashable]]:
        """ルーティングロジックを実行

        Args:
            state: 現在のグラフ状態
            config: 実行可能な設定

        Returns:
            次のノード名（Hashable）またはノード名のリスト
        """
