import os
from typing import List, Union, cast

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.types import Send
from src.prompts import query_writer_instructions
from pydantic import BaseModel, SecretStr
from src.schemas import SearchQueryList
from src.states import OverallState, WebSearchState
from src.utils import get_research_topic
from src.utils.date_utils import get_current_date
from src.config.configuration import Configuration

from .base_node import BaseNode

load_dotenv()


class QueryGenerationNode(BaseNode):
    """
    ユーザーの質問に基づいて検索クエリを生成するノード
    """

    def _get_query_count(self, state: OverallState, config_obj) -> int:
        """初期検索クエリ数を取得または設定。"""
        if state.initial_search_query_count is None:
            return config_obj.research.number_of_initial_queries
        return state.initial_search_query_count

    def _create_query_prompt(self, state: OverallState, query_count: int) -> str:
        """クエリ生成プロンプトを作成。"""
        current_date = get_current_date()
        research_topic = get_research_topic(state.messages)

        return query_writer_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            number_of_queries=query_count,
        )

    def _initialize_llm(self, config_obj) -> ChatOpenAI:
        """クエリ生成LLMを初期化。"""
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=config_obj.model.query_generator_model,
            temperature=config_obj.llm_parameters.query_generation_temperature,
            max_retries=config_obj.llm_parameters.max_retries,
            api_key=SecretStr(api_key) if api_key else None,
        )

    def _generate_queries(self, prompt: str, llm: ChatOpenAI) -> SearchQueryList:
        """検索クエリを生成。"""
        result = llm.with_structured_output(SearchQueryList).invoke(prompt)
        return cast(SearchQueryList, result)

    def _create_search_tasks(
        self, queries: List[str], state: OverallState
    ) -> List[Send]:
        """並列検索タスクを作成。"""
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
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """検索クエリを生成し、状態を更新。"""
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        # 設定を取得
        config_obj = Configuration.get_config(config)
        query_count = self._get_query_count(overall_state, config_obj)

        # プロンプトを作成し、LLMを初期化
        formatted_prompt = self._create_query_prompt(overall_state, query_count)
        llm = self._initialize_llm(config_obj)

        # クエリを生成
        query_result = self._generate_queries(formatted_prompt, llm)

        # 状態を更新して返す
        return OverallState(
            messages=overall_state.messages,
            search_query=query_result.query,
            web_research_result=overall_state.web_research_result,
            sources_gathered=overall_state.sources_gathered,
            initial_search_query_count=overall_state.initial_search_query_count,
            max_research_loops=overall_state.max_research_loops,
            research_loop_count=overall_state.research_loop_count,
            reasoning_model=overall_state.reasoning_model,
        )


class WebResearchRouterNode(BaseNode):
    """Web研究のルーティングを行うノード。"""

    def __init__(self):
        """Web研究ルーターノードを初期化。"""
        super().__init__()

    def _create_search_tasks(
        self, queries: List[str], state: OverallState
    ) -> List[Send]:
        """並列検索タスクを作成。"""
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
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """Web研究へのルーティングを決定。"""
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        # 検索クエリが存在する場合は並列検索タスクを作成
        if overall_state.search_query:
            return self._create_search_tasks(overall_state.search_query, overall_state)

        # 検索クエリが無い場合は終了
        return "finalize_answer"
