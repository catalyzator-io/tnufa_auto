import json, uuid
from typing import Protocol
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from fastembed import TextEmbedding
from src.utils.configs import QdrantConfig, EmbeddingConfig
from src.utils.models import EnhancedContent, EnhancedContentSection


class DatabasePopulatorProtocol(Protocol):
    def populate(self, entity_id: str, content: EnhancedContent):
        ...

class DatabasePopulator(DatabasePopulatorProtocol):
    """Populates vector database with enhanced content"""
    
    def __init__(
        self,
        qdrant_config: QdrantConfig,
        embedding_config: EmbeddingConfig
    ):
        """Initialize database populator with configurations
        
        Args:
            qdrant_config: Configuration for Qdrant connection and collection
            embedding_config: Configuration for embedding model
        """
        self.client = QdrantClient(**qdrant_config.model_dump(exclude={'collection'}))
        self.collection_name = qdrant_config.collection.name
        self.embedding_config = embedding_config
        self.embedder = TextEmbedding(self.embedding_config.model_name)
        
        self._init_collection()

    def _init_collection(self):
        """Initialize the Qdrant collection with proper schema"""
        # Use config for vector size and distance metric
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=self.embedding_config.vector_size,
                distance=self.embedding_config.distance_metric
            )
        )
        
        # Create payload index for title field
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="title",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD
        )
        # Create payload index for entity_id field to allow filtering by entity_id
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="entity_id",
            field_schema=qdrant_models.PayloadSchemaType.KEYWORD
        )

    def _create_points(
        self, 
        entity_id: str, 
        sections: list[EnhancedContentSection]
    ) -> list[qdrant_models.PointStruct]:
        """Create points for Qdrant from enhanced content sections"""
        embeddings = self.embedder.embed([section.summary for section in sections])
        
        return [
            qdrant_models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "entity_id": entity_id,
                    "title": section.title,
                    "summary": section.summary,
                    "notes": section.notes,
                    "analysis": section.analysis,
                    "actionable_gap_analysis": section.actionable_gap_analysis
                }
            )
            for section, embedding in zip(sections, embeddings)
        ]

    def _create_basic_info_section(self, basic_info: dict[str, str]) -> EnhancedContentSection:
        """Create a specialized section for basic info
        
        Args:
            basic_info: Dictionary containing basic entity information
            
        Returns:
            EnhancedContentSection: Section containing formatted basic info
        """
        return EnhancedContentSection(
            title="Others",
            summary=json.dumps(basic_info, indent=4),
            notes="Basic information about the entity",
            analysis="Collection of fundamental entity details",
            actionable_gap_analysis="Review and verify basic information completeness"
        )

    def populate(self, entity_id: str, content: EnhancedContent):
        """Populate database with enhanced content"""
        # Create basic info section
        basic_info_section = self._create_basic_info_section(content.basic_info)
        
        # Combine with other sections
        all_sections = [basic_info_section] + content.sections
        
        # Create points from all sections
        points = self._create_points(entity_id, all_sections)
        
        # Upsert points into collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
