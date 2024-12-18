from pathlib import Path

from src.ingestion.extract import ContentExtractor, AudioExtractor, DocumentExtractor
from src.ingestion.pipeline import IngestionPipeline
from src.ingestion.enhancement import ContentEnhancer
from src.ingestion.population import DatabasePopulator
from src.utils.llm_client import LLMClient

# TODO: improve dependency injection
def ingest(config_path: Path, entity_id: str, llm_client: LLMClient, form_id: str = "innovator_introduction"):
    """Convenience function for running the full pipeline"""
    content_extractor = ContentExtractor()
    content_extractor.register_extractor("audio", AudioExtractor())
    content_extractor.register_extractor("document", DocumentExtractor())
    content_enhancer = ContentEnhancer(llm_client)
    db_populator = DatabasePopulator()
    pipeline = IngestionPipeline(
        config_path,
        content_extractor,
        content_enhancer,
        db_populator,
        form_id
    )
    pipeline.process_entity(entity_id)

__all__ = ["ingest", "IngestionPipeline"]

