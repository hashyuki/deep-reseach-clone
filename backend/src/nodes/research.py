import os
from typing import Any, Dict, List, Tuple, Union, cast

from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.types import Send
from src.prompts import reflection_instructions
from pydantic import BaseModel, SecretStr
from src.schemas import Reflection
from src.states import OverallState, WebSearchState
from src.utils import get_research_topic
from src.utils.date_utils import get_current_date
from src.config.configuration import Configuration

from .base_node import BaseNode

load_dotenv()

if os.getenv("TAVILY_API_KEY") is None:
    raise ValueError("TAVILY_API_KEY が設定されていません")


class WebResearchNode(BaseNode):
    """TavilySearchツールを使用してウェブ研究を実行するノード。"""

    def __init__(self):
        """ウェブ研究ノードを初期化。"""
        super().__init__()

    def _get_tavily_search(self, config_obj) -> TavilySearchResults:
        """設定に基づいてTavilySearchResultsインスタンスを作成。"""
        return TavilySearchResults(
            max_results=config_obj.search.max_results,
            search_depth=config_obj.search.depth,
            include_answer=True,
            include_raw_content=False,
            include_images=config_obj.search.include_images,
            api_key=os.getenv("TAVILY_API_KEY"),
        )

    def _execute_search(self, query: str, config_obj) -> List[Dict[str, Any]]:
        """Tavily検索を実行して生の結果を返す。"""
        tavily_search = self._get_tavily_search(config_obj)
        return tavily_search.invoke({"query": query})

    def _create_citation_marker(self, state_id: int, result_index: int) -> str:
        """検索結果の引用マーカーを作成。"""
        return f"【{state_id}-{result_index + 1}】"

    def _format_source(
        self, result: Dict[str, Any], citation_marker: str
    ) -> Dict[str, str]:
        """単一の検索結果をソースオブジェクトにフォーマット。"""
        return {
            "short_url": citation_marker,
            "value": result["url"],
            "title": result.get("title", ""),
            "content": result.get("content", ""),
        }

    def _format_result_text(self, result: Dict[str, Any], citation_marker: str) -> str:
        """単一の検索結果を表示テキストにフォーマット。"""
        title = result.get("title", "タイトルなし")
        content = result.get("content", "コンテンツなし")
        url = result.get("url", "")

        # 明確な引用マーカー付きフォーマット
        return f"Source {citation_marker}:\nTitle: {title}\nContent: {content}\nURL: {url}\n\n引用時は必ず {citation_marker} を使用してください。\n\n"

    def _process_search_results(
        self, search_results: List[Dict[str, Any]], state_id: int
    ) -> Tuple[List[Dict[str, str]], str]:
        """検索結果を処理してソースとフォーマット済みテキストを返す。"""
        sources_gathered = []
        formatted_results = []

        for idx, result in enumerate(search_results):
            citation_marker = self._create_citation_marker(state_id, idx)

            # ソースに追加
            source = self._format_source(result, citation_marker)
            sources_gathered.append(source)

            # 結果テキストをフォーマット
            result_text = self._format_result_text(result, citation_marker)
            formatted_results.append(result_text)

        return sources_gathered, "".join(formatted_results)

    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """TavilySearchツールを使用してウェブ研究を実行。"""
        # 型安全性のためにstateをWebSearchStateとしてキャスト
        web_search_state = cast(WebSearchState, state)

        # 設定を取得
        config_obj = Configuration.get_config(config)

        # 検索を実行
        search_results = self._execute_search(web_search_state.search_query, config_obj)

        # 結果を処理
        sources_gathered, modified_text = self._process_search_results(
            search_results, web_search_state.id
        )

        # 新しい状態オブジェクトを作成
        return OverallState(
            messages=[],
            search_query=[web_search_state.search_query],
            web_research_result=[modified_text],
            sources_gathered=sources_gathered,
            initial_search_query_count=None,
            max_research_loops=None,
            research_loop_count=0,
            reasoning_model=None,
        )


class ReflectionNode(BaseNode):
    """研究結果を分析し、知識のギャップを特定するノード。"""

    def __init__(self):
        """リフレクションノードを初期化。"""
        super().__init__()

    def _get_reasoning_model(self, state: OverallState, config_obj) -> str:
        """状態または設定から推論モデルを取得。"""
        return state.reasoning_model or config_obj.model.reflection_model

    def _create_reflection_prompt(self, state: OverallState) -> str:
        """状態データからリフレクションプロンプトを作成。"""
        current_date = get_current_date()
        research_topic = get_research_topic(state.messages)
        summaries = "\n\n---\n\n".join(state.web_research_result)

        return reflection_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            summaries=summaries,
        )

    def _initialize_llm(self, model: str, config_obj) -> ChatOpenAI:
        """推論LLMを初期化。"""
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=model,
            temperature=config_obj.llm_parameters.reflection_temperature,
            max_retries=config_obj.llm_parameters.max_retries,
            api_key=SecretStr(api_key) if api_key else None,
        )

    def _analyze_research_gaps(self, prompt: str, llm: ChatOpenAI) -> Reflection:
        """研究を分析し、知識のギャップを特定。"""
        result = llm.with_structured_output(Reflection).invoke(prompt)
        return cast(Reflection, result)

    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """知識のギャップを特定し、フォローアップクエリを生成。"""
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        # 設定を取得
        config_obj = Configuration.get_config(config)
        reasoning_model = self._get_reasoning_model(overall_state, config_obj)
        current_loop_count = overall_state.research_loop_count + 1

        # プロンプトを作成し、LLMを初期化
        formatted_prompt = self._create_reflection_prompt(overall_state)
        llm = self._initialize_llm(reasoning_model, config_obj)

        # ギャップを分析
        _result = self._analyze_research_gaps(formatted_prompt, llm)

        # 状態を更新して返す
        return OverallState(
            messages=overall_state.messages,
            search_query=overall_state.search_query,
            web_research_result=overall_state.web_research_result,
            sources_gathered=overall_state.sources_gathered,
            initial_search_query_count=overall_state.initial_search_query_count,
            max_research_loops=overall_state.max_research_loops,
            research_loop_count=current_loop_count,
            reasoning_model=reasoning_model,
        )


class ResearchEvaluationNode(BaseNode):
    """研究の進捗を評価し、次のステップを決定するノード。"""

    def __init__(self):
        """研究評価ノードを初期化。"""
        super().__init__()

    def _get_max_research_loops(self, state: OverallState, config_obj) -> int:
        """状態または設定から最大研究ループ数を取得。"""
        return (
            state.max_research_loops
            if state.max_research_loops is not None
            else config_obj.research.max_research_loops
        )

    def _should_finalize_research(self, state: OverallState, max_loops: int) -> bool:
        """研究を終了すべきかどうかを判断。"""
        return state.research_loop_count >= max_loops

    def _create_follow_up_searches(self, state: OverallState, config_obj) -> List[Send]:
        """知識ギャップのフォローアップ検索タスクを作成。"""
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
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """研究フローの次のステップを決定。"""
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        # 設定を取得
        config_obj = Configuration.get_config(config)
        max_research_loops = self._get_max_research_loops(overall_state, config_obj)

        if self._should_finalize_research(overall_state, max_research_loops):
            return "finalize_answer"
        else:
            return self._create_follow_up_searches(overall_state, config_obj)
