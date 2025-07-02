from typing import Optional
from dataclasses import dataclass, replace
from copy import deepcopy

from langchain_core.runnables import RunnableConfig


@dataclass
class ModelConfig:
    """LLMモデル設定"""
    query_generator_model: str = "gpt-4o"
    reflection_model: str = "gpt-4o"
    answer_model: str = "gpt-4o"


@dataclass
class ResearchConfig:
    """研究プロセス設定"""
    number_of_initial_queries: int = 3
    max_research_loops: int = 2
    max_follow_up_queries: int = 3


@dataclass
class LLMParameterConfig:
    """LLMパラメータ設定"""
    query_generation_temperature: float = 1.0
    reflection_temperature: float = 1.0
    answer_generation_temperature: float = 0.0
    max_retries: int = 2


@dataclass
class SearchConfig:
    """検索設定"""
    max_results: int = 5
    depth: str = "advanced"
    include_images: bool = False


@dataclass
class CitationConfig:
    """引用設定"""
    title_max_length: int = 50


class Configuration:
    """設定管理クラス"""
    
    def __init__(self):
        # デフォルト設定
        self.model = ModelConfig()
        self.research = ResearchConfig()
        self.llm_parameters = LLMParameterConfig()
        self.search = SearchConfig()
        self.citation = CitationConfig()

    def override_with_runnable_config(self, config: Optional[RunnableConfig]) -> 'Configuration':
        """実行時設定でオーバーライドした新しいConfigurationを返す"""
        if not config or "configurable" not in config:
            return deepcopy(self)
        
        configurable = config["configurable"]
        new_config = Configuration()
        
        # 現在の設定をコピー
        new_config.model = replace(self.model)
        new_config.research = replace(self.research)
        new_config.llm_parameters = replace(self.llm_parameters)
        new_config.search = replace(self.search)
        new_config.citation = replace(self.citation)
        
        # 各設定セクションを一括更新
        sections = [
            ("model", new_config.model),
            ("research", new_config.research), 
            ("llm_parameters", new_config.llm_parameters),
            ("search", new_config.search),
            ("citation", new_config.citation)
        ]
        
        for section_name, section_obj in sections:
            # dataclassのフィールドと一致するkeyを探して更新
            field_names = {f.name for f in section_obj.__dataclass_fields__.values()}
            updates = {key: value for key, value in configurable.items() if key in field_names}
            
            if updates:
                setattr(new_config, section_name, replace(section_obj, **updates))
        
        return new_config

    @classmethod
    def get_config(cls, runnable_config: Optional[RunnableConfig] = None) -> 'Configuration':
        """設定を取得（実行時オーバーライドを含む）"""
        if not hasattr(cls, '_default_config') or cls._default_config is None:
            cls._default_config = cls()
        
        if runnable_config is None:
            return cls._default_config
        
        return cls._default_config.override_with_runnable_config(runnable_config)


