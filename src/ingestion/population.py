from typing import Protocol, Optional
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from fastembed import TextEmbedding
from src.utils.models import EnhancedContent, EnhancedContentSection

class EmbeddingConfig(BaseModel):
    """Configuration for embedding settings"""
    model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    vector_size: int = 384
    distance_metric: qdrant_models.Distance = qdrant_models.Distance.COSINE

class QdrantConfig(BaseModel):
    """Configuration for Qdrant connection settings"""
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    timeout: float = 10.0
    prefer_grpc: bool = False

class DatabasePopulatorProtocol(Protocol):
    def populate(self, entity_id: str, data: EnhancedContent):
        ...

class DatabasePopulator(DatabasePopulatorProtocol):
    """Populates Qdrant vector database with enhanced content sections"""
    
    def __init__(
        self, 
        collection_name: str = "catalyzator",
        qdrant_config: QdrantConfig = None,
        embedding_config: EmbeddingConfig = None
    ):
        # Initialize configs with defaults if not provided
        self.collection_name = collection_name
        self.qdrant_config = qdrant_config or QdrantConfig()
        self.embedding_config = embedding_config or EmbeddingConfig()
        
        # Initialize Qdrant client with config
        self.client = QdrantClient(**self.qdrant_config.model_dump())
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
                id=f"{entity_id}_{idx}",
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
            for idx, (section, embedding) in enumerate(zip(sections, embeddings))
        ]

    def _create_basic_info_section(self, basic_info: dict[str, str]) -> EnhancedContentSection:
        """Create a specialized section for basic info
        
        Args:
            basic_info: Dictionary containing basic entity information
            
        Returns:
            EnhancedContentSection: Section containing formatted basic info
        """
        return EnhancedContentSection(
            title="others",
            summary="\n".join(f"{k}: {v}" for k, v in basic_info.items()),
            notes="Basic information about the entity",
            analysis="Collection of fundamental entity details",
            actionable_gap_analysis="Review and verify basic information completeness"
        )

    def populate(self, entity_id: str, data: EnhancedContent):
        """Populate Qdrant with enhanced content sections
        
        Args:
            entity_id: Unique identifier for the entity
            data: Enhanced content data containing sections
        """
        # Create basic info section
        basic_info_section = self._create_basic_info_section(data.basic_info)
        
        # Combine with other sections
        all_sections = [basic_info_section] + data.sections
        
        # Create points from all sections
        points = self._create_points(entity_id, all_sections)
        
        # Upsert points into collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
