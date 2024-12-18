from dataclasses import dataclass
from typing import Optional

from grant_answering.prompts import PromptBuilder
from src.utils.configs import AppConfig
from src.utils.llm_client import LLMClient
from src.utils.qdrant_access import QdrantAccess, QdrantFilter
from src.grant_answering.innovator_profile_provider import InnovatorProfileProvider
from src.grant_answering.grant_answering import GrantAnswering

@dataclass
class Container:
    """Dependency injection container for grant answering"""
    config: AppConfig
    llm_client: Optional[LLMClient] = None
    qdrant_access: Optional[QdrantAccess] = None
    qdrant_filter: Optional[QdrantFilter] = None
    prompt_builder: Optional[PromptBuilder] = None
    profile_provider: Optional[InnovatorProfileProvider] = None
    
    def __post_init__(self):
        # Initialize LLM client if not provided
        if not self.llm_client:
            self.llm_client = LLMClient(**self.config.llm.model_dump(exclude={"collection"}))
            
        # Initialize Qdrant access if not provided
        if not self.qdrant_access:
            self.qdrant_access = QdrantAccess(
                qdrant_config=self.config.qdrant,
                embedding_config=self.config.embedding
            )
            
        # Initialize profile provider if not provided
        if not self.profile_provider:
            self.profile_provider = InnovatorProfileProvider(
                collection_name=self.config.qdrant.collection.name,
                llm_client=self.llm_client,
                qdrant=self.qdrant_access,
                filter_builder=QdrantFilter(),
                search_config=self.config.search
            )
            
        # Initialize prompt builder if not provided
        if not self.prompt_builder:
            self.prompt_builder = PromptBuilder()
            
    def create_grant_answering(self) -> GrantAnswering:
        return GrantAnswering(
            llm_client=self.llm_client,
            prompt_builder=self.prompt_builder,
            profile_provider=self.profile_provider
        )
        