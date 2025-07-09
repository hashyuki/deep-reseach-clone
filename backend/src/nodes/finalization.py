import os
from typing import Dict, List, Tuple, Union, cast

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.types import Send
from pydantic import BaseModel, SecretStr

from src.config.configuration import Configuration
from src.prompts import answer_instructions
from src.states import OverallState
from src.utils import get_research_topic
from src.utils.date_utils import get_current_date
from .base_node import BaseNode

load_dotenv()


class FinalizationNode(BaseNode):
    """
    研究結果を包括的な回答にまとめるノード
    """

    def _get_reasoning_model(self, state: OverallState, config_obj) -> str:
        """状態または設定から推論モデルを取得。"""
        return state.reasoning_model or config_obj.model.answer_model

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

    def _initialize_llm(self, model: str, config_obj) -> ChatOpenAI:
        """推論モデルを初期化。"""
        api_key = os.getenv("OPENAI_API_KEY")
        return ChatOpenAI(
            model=model,
            temperature=config_obj.llm_parameters.answer_generation_temperature,
            max_retries=config_obj.llm_parameters.max_retries,
            api_key=SecretStr(api_key) if api_key else None,
        )

    def _process_citations(
        self, sources: List[Dict[str, str]], config_obj
    ) -> Dict[str, Tuple[str, str]]:
        """引用ソースを処理して表示用のマッピングを作成。"""
        citation_mapping = {}
        max_title_length = config_obj.citation.title_max_length

        for source in sources:
            short_url = source.get("short_url", "")
            title = source.get("title", "タイトルなし")
            url = source.get("value", "")

            # タイトルの長さを制限
            if len(title) > max_title_length:
                display_title = title[: max_title_length - 3] + "..."
            else:
                display_title = title

            citation_mapping[short_url] = (display_title, url)

        return citation_mapping

    def _replace_citations_with_links(
        self, text: str, citation_mapping: Dict[str, Tuple[str, str]]
    ) -> str:
        """テキスト内の引用マーカーをマークダウンリンクに変換。"""
        for marker, (title, url) in citation_mapping.items():
            # 【1-1】形式のマーカーを[title](url)に置換
            text = text.replace(marker, f"[{title}]({url})")

        return text

    def _generate_comprehensive_answer(self, prompt: str, llm: ChatOpenAI) -> str:
        """包括的な回答を生成。"""
        result = llm.invoke(prompt)
        return result.content

    def __call__(
        self, state: Union[BaseModel, List[Send], str], config: RunnableConfig
    ) -> Union[BaseModel, List[Send], str]:
        """研究結果から最終的な包括回答を生成。"""
        # 型安全性のためにstateをOverallStateとしてキャスト
        overall_state = cast(OverallState, state)

        # 設定を取得
        config_obj = Configuration.get_config(config)
        reasoning_model = self._get_reasoning_model(overall_state, config_obj)

        # プロンプトを作成し、LLMを初期化
        formatted_prompt = self._create_final_prompt(overall_state)
        llm = self._initialize_llm(reasoning_model, config_obj)

        # 包括的な回答を生成
        comprehensive_answer = self._generate_comprehensive_answer(
            formatted_prompt, llm
        )

        # 引用を処理
        citation_mapping = self._process_citations(
            overall_state.sources_gathered, config_obj
        )

        # 引用マーカーをマークダウンリンクに変換
        final_answer = self._replace_citations_with_links(
            comprehensive_answer, citation_mapping
        )

        # 最終的なAIメッセージを作成
        ai_message = AIMessage(content=final_answer)

        # 更新された状態を返す
        return OverallState(
            messages=overall_state.messages + [ai_message],
            search_query=overall_state.search_query,
            web_research_result=overall_state.web_research_result,
            sources_gathered=overall_state.sources_gathered,
            initial_search_query_count=overall_state.initial_search_query_count,
            max_research_loops=overall_state.max_research_loops,
            research_loop_count=overall_state.research_loop_count,
            reasoning_model=overall_state.reasoning_model,
        )
