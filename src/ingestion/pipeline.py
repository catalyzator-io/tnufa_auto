from pathlib import Path
from src.ingestion.enhancement import ContentEnhancerProtocol
from src.ingestion.extract.base import ContentExtractorProtocol
from src.ingestion.form_collection import FormCollector
from src.ingestion.population import DatabasePopulatorProtocol


class IngestionPipeline:
    """Coordinates the ingestion pipeline stages"""
    
    def __init__(
        self,
        config_path: Path,
        content_extractor: ContentExtractorProtocol,
        content_enhancer: ContentEnhancerProtocol,
        db_populator: DatabasePopulatorProtocol,
        form_id: str = "innovator_introduction"
    ):
        self.content_extractor = content_extractor
        self.content_enhancer = content_enhancer
        self.db_populator = db_populator
        self.form_collector = FormCollector(config_path, self.content_extractor, form_id)
        
    def process_entity(self, entity_id: str):
        """Process a single entity through the full pipeline"""
        # 1. Collect form data
        raw_data = self.form_collector.collect_form_data(entity_id)
        # 2. Enhance content
        enhanced_data = self.content_enhancer.process_content(raw_data)
        # 3. Populate database
        self.db_populator.populate(entity_id, enhanced_data)