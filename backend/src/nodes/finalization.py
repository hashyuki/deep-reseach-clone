import os
from typing import Any, Dict, List, Tuple, Union, cast

from config import Configuration
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.types import Send
from prompts import answer_instructions, get_current_date
from pydantic import BaseModel, SecretStr
from states import OverallState
from utils import get_research_topic

from .base_node import BaseNode

load_dotenv()


class FinalizationNode(BaseNode):
    """研究結果を包括的な回答にまとめるノード。"""

    def __init__(self):
        """最終化ノードを初期化。"""
        super().__init__()

    def _get_reasoning_model(self, state: OverallState, config: RunnableConfig) -> str:
        """状態または設定から推論モデルを取得。"""
        configurable = Configuration.from_runnable_config(config)
        return state.reasoning_model or configurable.answer_model

    def _create_final_prompt(self, state: OverallState) -> str:
        """最終回答生成用のプロンプトを作成。"""
        current_date = get_current_date()
        research_topic = get_research_topic(state.messages)
        summaries = "\n---\n\n".join(state.web_research_result)

        return answer_instructions.format(
            current_date=current_date,
            research_topic=research_topic,
            summaries=summaries,
        )

    def _initialize_llm(self, model: str) -> ChatOpenAI:
        """推論モデルを初期化。"""
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=model,
            temperature=0,
            max_retries=2,
            api_key=SecretStr(api_key) if api_key else None,
        )

    def _generate_final_answer(self, prompt: str, llm: ChatOpenAI) -> str:
        """最終回答を生成。"""
        # ストリーミングを無効にして完全な回答を一度に生成
        llm.streaming = False
        result = llm.invoke(prompt)
        # LLMレスポンスのcontent属性を安全に取得
        if hasattr(result, "content"):
            return str(result.content)
        else:
            return str(result)

    def _process_citations(
        self, answer_content: str, sources: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """引用を処理し、マークダウンリンク形式に変換。"""
        processed_content = answer_content
        unique_sources = []
        
        for source in sources:
            short_url = source.get("short_url", "")
            title = source.get("title", "参照")
            url = source.get("value", "")
            
            if short_url and short_url in processed_content:
                # タイトルを短縮（長すぎる場合）
                display_title = title
                if len(display_title) > 50:
                    display_title = display_title[:47] + "..."
                
                markdown_link = f"[{display_title}]({url})"
                
                # マーカーをマークダウンリンクに置換
                processed_content = processed_content.replace(short_url, markdown_link)
                unique_sources.append(source)

        return processed_content, unique_sources

    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """研究要約を最終化。

        ソースの重複除去とフォーマットにより最終出力を準備し、
        実行中の要約と組み合わせて適切な引用を含む
        構造化された研究レポートを作成する。

        Args:
            state: 実行中の要約と収集されたソースを含む現在のグラフ状態
            config: LLMプロバイダー設定を含む実行可能な設定

        Returns:
            ソースを含む最終要約を含むrunning_summaryキーを持つ状態更新辞書
        """
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        # 推論モデルを取得
        reasoning_model = self._get_reasoning_model(overall_state, config)

        # プロンプトを作成
        formatted_prompt = self._create_final_prompt(overall_state)

        # LLMを初期化
        llm = self._initialize_llm(reasoning_model)

        # 最終回答を生成
        answer_content = self._generate_final_answer(formatted_prompt, llm)

        # 引用を処理
        processed_content, unique_sources = self._process_citations(
            answer_content, overall_state.sources_gathered
        )

        # 新しい状態オブジェクトを作成して返す
        return OverallState(
            messages=overall_state.messages + [AIMessage(content=processed_content)],
            search_query=overall_state.search_query,
            web_research_result=overall_state.web_research_result,
            sources_gathered=overall_state.sources_gathered + unique_sources,
            initial_search_query_count=overall_state.initial_search_query_count,
            max_research_loops=overall_state.max_research_loops,
            research_loop_count=overall_state.research_loop_count,
            reasoning_model=overall_state.reasoning_model,
        )
