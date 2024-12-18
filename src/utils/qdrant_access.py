from typing import Protocol, Any, Optional, Sequence
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from src.utils.configs import QdrantConfig
from src.utils.models import QdrantPoint

class QdrantFilter(Protocol):
    """Protocol for Qdrant filters"""
    def add(self, field: str, value: Any) -> 'QdrantFilter':
        """Add equals condition"""
        ...
    
    def add_any(self, field: str, values: Sequence[Any]) -> 'QdrantFilter':
        """Add matches any condition"""
        ...
    
    def combine(self, other: 'QdrantFilter') -> 'QdrantFilter':
        """Combine with another filter"""
        ...
    
    def build(self) -> qdrant_models.Filter:
        """Build the filter"""
        ...

class QdrantAccess(Protocol):
    """Protocol for Qdrant database access"""
    def search(
        self,
        collection: str,
        query_vector: list[float],
        filters: Optional[QdrantFilter] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> list[QdrantPoint]:
        """Search points by vector similarity"""
        ...
    
    def filter(
        self,
        collection: str,
        filters: QdrantFilter,
        limit: Optional[int] = None
    ) -> list[QdrantPoint]:
        """Get points matching filter criteria"""
        ...

class DefaultQdrantFilter:
    """Default implementation of QdrantFilter"""
    def __init__(self):
        self.conditions = []
    
    def add(self, field: str, value: Any) -> 'DefaultQdrantFilter':
        self.conditions.append(
            qdrant_models.FieldCondition(
                key=field,
                match=qdrant_models.MatchValue(value=value)
            )
        )
        return self
    
    def add_any(self, field: str, values: Sequence[Any]) -> 'DefaultQdrantFilter':
        self.conditions.append(
            qdrant_models.FieldCondition(
                key=field,
                match=qdrant_models.MatchAny(any=values)
            )
        )
        return self
    
    def combine(self, other: 'DefaultQdrantFilter') -> 'DefaultQdrantFilter':
        self.conditions.extend(other.conditions)
        return self
    
    def build(self) -> qdrant_models.Filter:
        return qdrant_models.Filter(must=self.conditions) if self.conditions else None

class QdrantProvider:
    """Default implementation of Qdrant access"""
    def __init__(self, config: Optional[QdrantConfig] = None):
        self.client = QdrantClient(**config.model_dump(exclude={'collection'}))
    
    def search(
        self,
        collection: str,
        query_vector: list[float],
        filters: Optional[QdrantFilter] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> list[QdrantPoint]:
        search_result = self.client.query_points(
            collection_name=collection,
            query=qdrant_models.QueryRequest(
                vector=query_vector,
                filter=filters.build() if filters else None,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=True
            )
        )
        return [
            QdrantPoint(
                payload=point.payload,
                vector=point.vector,
                score=point.score
            ) for point in search_result
        ]
    
    def filter(
        self,
        collection: str,
        filters: QdrantFilter,
        limit: Optional[int] = None
    ) -> list[QdrantPoint]:
        scroll_result = self.client.scroll(
            collection_name=collection,
            scroll_filter=filters.build(),
            limit=limit,
            with_payload=True,
            with_vectors=True
        )[0]
        return [
            QdrantPoint(
                payload=point.payload,
                vector=point.vector
            ) for point in scroll_result
        ]