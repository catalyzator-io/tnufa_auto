from dataclasses import dataclass
from typing import Optional

from src.utils.configs import AppConfig
from src.utils.llm_client import LLMClient
from src.ingestion.extract import ContentExtractor, AudioExtractor, DocumentExtractor
from src.ingestion.enhancement import ContentEnhancer
from src.ingestion.population import DatabasePopulator
from src.utils.form_access import FirebaseFormProvider
from src.ingestion.pipeline import IngestionPipeline

@dataclass
class Container:
    """Dependency injection container"""
    config: AppConfig
    llm_client: Optional[LLMClient] = None
    form_provider: Optional[FirebaseFormProvider] = None
    content_extractor: Optional[ContentExtractor] = None
    content_enhancer: Optional[ContentEnhancer] = None
    db_populator: Optional[DatabasePopulator] = None

    def __post_init__(self):
        # Initialize LLM client
        if not self.llm_client:
            self.llm_client = LLMClient(**self.config.llm.model_dump())

        # Initialize form provider
        if not self.form_provider:
            self.form_provider = FirebaseFormProvider(self.config.firebase)

        # Initialize content extractor
        if not self.content_extractor:
            self.content_extractor = ContentExtractor()
            self.content_extractor.register_extractor("audio", AudioExtractor())
            self.content_extractor.register_extractor("document", DocumentExtractor())

        # Initialize content enhancer
        if not self.content_enhancer:
            self.content_enhancer = ContentEnhancer(self.llm_client)

        # Initialize database populator
        if not self.db_populator:
            self.db_populator = DatabasePopulator(
                qdrant_config=self.config.qdrant,
                embedding_config=self.config.embedding
            )

    def create_pipeline(self, form_id: str = "innovator_introduction") -> IngestionPipeline:
        """Create an ingestion pipeline with all dependencies"""
        return IngestionPipeline(
            storage_provider=self.form_provider,
            database_provider=self.form_provider,
            content_extractor=self.content_extractor,
            content_enhancer=self.content_enhancer,
            db_populator=self.db_populator,
            form_id=form_id
        ) 