from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field
from qdrant_client.http import models as qdrant_models


class QdrantCollectionConfig(BaseModel):
    """Configuration for Qdrant collection settings"""
    name: str = "catalyzator"
    recreate_collection: bool = False
    on_disk_payload: bool = True


class QdrantConfig(BaseModel):
    """Configuration for Qdrant connection and collection settings"""
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    timeout: float = 10.0
    prefer_grpc: bool = False
    collection: QdrantCollectionConfig = QdrantCollectionConfig()


class FirebaseConfig(BaseModel):
    """Configuration for Firebase connection settings"""
    credentials_path: Path
    storage_bucket: str = "catalyzator.appspot.com"
    default_form_id: str = "innovator_introduction"


class SearchConfig(BaseModel):
    """Configuration for search parameters"""
    min_relevance_score: float = Field(default=0.6, description="Minimum relevance score for sections")
    max_sections: int = Field(default=3, description="Maximum number of sections to return")
    include_taxonomy_terms: bool = Field(default=True, description="Whether to include taxonomy terms in search")

class EmbeddingConfig(BaseModel):
    """Configuration for embedding settings"""
    model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'
    vector_size: int = 384
    distance_metric: qdrant_models.Distance = qdrant_models.Distance.COSINE

class LLMConfig(BaseModel):
    """Configuration for LLM client settings"""
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class AppConfig(BaseModel):
    """Root configuration containing all sub-configurations"""
    firebase: FirebaseConfig
    qdrant: QdrantConfig
    llm: LLMConfig
    embedding: EmbeddingConfig
    search: SearchConfig

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        return cls(
            firebase=FirebaseConfig(
                credentials_path=Path(os.getenv('FIREBASE_CREDENTIALS_PATH', 'config.json')),
                storage_bucket=os.getenv('FIREBASE_STORAGE_BUCKET', 'catalyzator.appspot.com')
            ),
            qdrant=QdrantConfig(
                url=os.getenv('QDRANT_URL', 'http://localhost:6333'),
                api_key=os.getenv('QDRANT_API_KEY'),
                collection=QdrantCollectionConfig(
                    name=os.getenv('QDRANT_COLLECTION', 'catalyzator')
                )
            ),
            llm=LLMConfig(
                api_key=os.getenv('OPENAI_API_KEY', ''),
                model=os.getenv('OPENAI_MODEL', 'gpt-4')
            ),
            embedding=EmbeddingConfig(
                model_name=os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            ),
            search=SearchConfig()
        )

    @classmethod
    def from_json(cls, path: Path) -> 'AppConfig':
        """Create configuration from JSON file"""
        import json
        
        with open(path) as f:
            config_dict = json.load(f)
            return cls(**config_dict)