import os
from typing import List, Union, cast

from config import Configuration
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.types import Send
from prompts import get_current_date, query_writer_instructions
from pydantic import BaseModel, SecretStr
from schemas import SearchQueryList
from states import OverallState, WebSearchState
from utils import get_research_topic

from .base_node import BaseNode

load_dotenv()


class QueryGenerationNode(BaseNode):
    """ユーザーの質問に基づいて検索クエリを生成するノード。"""

    def __init__(self):
        """クエリ生成ノードを初期化。"""
        super().__init__()

    def _get_query_count(self, state: OverallState, configurable: Configuration) -> int:
        """初期検索クエリ数を取得または設定。"""
        if state.initial_search_query_count is None:
            return configurable.number_of_initial_queries
        return state.initial_search_query_count

    def _initialize_llm(self, model: str) -> ChatOpenAI:
        """OpenAI LLMを初期化。"""
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=model,
            temperature=1.0,
            max_retries=2,
            api_key=SecretStr(api_key) if api_key else None,
        )

    def _create_query_prompt(self, state: OverallState, query_count: int) -> str:
        """クエリ生成用のプロンプトを作成。"""
        current_date = get_current_date()
        research_topic = get_research_topic(state.messages)

        return query_writer_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            number_queries=query_count,
        )

    def _generate_queries(self, prompt: str, llm: ChatOpenAI) -> List[str]:
        """構造化出力を使用して検索クエリを生成。"""
        structured_llm = llm.with_structured_output(SearchQueryList)
        result = structured_llm.invoke(prompt)
        typed_result = cast(SearchQueryList, result)
        return typed_result.query

    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """ユーザーの質問に基づいて検索クエリを生成。

        OpenAIを使用してユーザーの質問に基づいたウェブ研究用の
        最適化された検索クエリを作成する。

        Args:
            state: ユーザーの質問を含む現在のグラフ状態
            config: LLMプロバイダー設定を含む実行可能な設定

        Returns:
            生成されたクエリを含むsearch_queryキーを持つ状態更新辞書
        """
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        configurable = Configuration.from_runnable_config(config)

        # 初期検索クエリ数を取得
        query_count = self._get_query_count(overall_state, configurable)

        # LLMを初期化
        llm = self._initialize_llm(configurable.query_generator_model)

        # プロンプトを作成
        formatted_prompt = self._create_query_prompt(overall_state, query_count)

        # 検索クエリを生成
        queries = self._generate_queries(formatted_prompt, llm)

        # 既存の状態を更新して返す
        return OverallState(
            messages=overall_state.messages,
            search_query=overall_state.search_query + queries,
            web_research_result=overall_state.web_research_result,
            sources_gathered=overall_state.sources_gathered,
            initial_search_query_count=query_count,
            max_research_loops=overall_state.max_research_loops,
            research_loop_count=overall_state.research_loop_count,
            reasoning_model=overall_state.reasoning_model,
        )


class WebResearchRouterNode(BaseNode):
    """検索クエリをウェブ研究ノードにルーティングするノード。"""

    def __init__(self):
        """ウェブ研究ルーターノードを初期化。"""
        super().__init__()

    def _create_search_tasks(self, queries: List[str]) -> List[Send]:
        """各検索クエリに対してウェブ研究タスクを作成。"""
        return [
            Send("web_research", WebSearchState(search_query=search_query, id=int(idx)))
            for idx, search_query in enumerate(queries)
        ]

    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """検索クエリをウェブ研究ノードに送信。

        これは各検索クエリに対してn個のウェブ研究ノードを
        スポーンするために使用される。

        Args:
            state: 検索クエリを含む現在のグラフ状態
            config: 実行可能な設定

        Returns:
            並列ウェブ研究実行用のSendオブジェクトのリスト
        """
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)
        return self._create_search_tasks(overall_state.search_query)
