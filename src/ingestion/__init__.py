from src.ingestion.pipeline import IngestionPipeline
from src.utils.configs import AppConfig
from src.ingestion.container import Container as IngestionContainer

def ingest(
    config: AppConfig,
    entity_id: str,
    form_id: str = "innovator_introduction"
):
    """Convenience function for running the full pipeline"""
    container = IngestionContainer(config)
    pipeline = container.create_pipeline(form_id)
    pipeline.process_entity(entity_id)

__all__ = ["ingest", "IngestionPipeline", "IngestionContainer"]
