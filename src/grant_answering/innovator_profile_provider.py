from typing import Optional, get_args
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from fastembed import TextEmbedding
from pydantic import BaseModel, Field
from src.utils.taxonomy import taxonomy, section_info
from src.utils.models import GrantQuestion, SectionTitle

class SearchConfig(BaseModel):
    """Configuration for search parameters"""
    min_relevance_score: float = Field(default=0.6, description="Minimum relevance score for sections")
    max_sections: int = Field(default=3, description="Maximum number of sections to return")
    include_taxonomy_terms: bool = Field(default=True, description="Whether to include taxonomy terms in search")

class InnovatorProfileProvider:
    """Provides relevant innovator profile information for answering grant questions"""
    
    def __init__(
        self,
        collection_name: str = "catalyzator",
        qdrant_url: str = "http://localhost:6333",
        search_config: Optional[SearchConfig] = None
    ):
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedder = TextEmbedding('sentence-transformers/all-MiniLM-L6-v2')
        self.search_config = search_config or SearchConfig()
        
        # Create taxonomy category to section title mapping
        self._category_section_mapping = self._build_category_mapping()

    def _build_category_mapping(self) -> dict[str, list[SectionTitle]]:
        """Build mapping from taxonomy categories to relevant section titles"""
        mapping = {
            "TEAM_LEADERSHIP": ["Team and Leadership"],
            "COMPANY_FUNDAMENTALS": ["Introduction", "Others"],
            "PRODUCT_TECHNOLOGY": ["The Solution", "Technology/Innovation"],
            "MARKET_ANALYSIS": ["Market Opportunity", "Competitive Analysis"],
            "BUSINESS_MODEL": ["The Business Model"],
            "TRACTION_VALIDATION": ["Traction and Validation"],
            "FINANCIAL_INFORMATION": ["Financial Information"],
            "DEVELOPMENT_EXECUTION": ["Development and Executor"],
            "LEGAL_COMPLIANCE": ["Legal and Compliance"],
            "IMPACT_INNOVATION": ["Impact and Innovation"]
        }
        return mapping

    def _get_relevant_section_titles(self, question: GrantQuestion) -> list[str]:
        """Map question to relevant section titles using taxonomy and question metadata
        
        Args:
            question: The grant question to find relevant sections for
            
        Returns:
            list of relevant section titles to search in
        """
        relevant_titles = set()
        
        # Check question category against taxonomy
        question_text = f"{question.category} {question.title} {question.question}"
        question_lower = question_text.lower()
        
        # Add titles based on taxonomy term matches
        for category, terms in taxonomy.items():
            if any(term.lower() in question_lower for term in terms):
                if category in self._category_section_mapping:
                    relevant_titles.update(title.value for title in self._category_section_mapping[category])
        
        # Add titles based on section info descriptions
        for title, description in section_info.items():
            if any(term.lower() in question_lower for term in description.lower().split()):
                relevant_titles.add(title)
        
        return list(relevant_titles or get_args(SectionTitle))

    def get_relevant_context(
        self,
        entity_id: str,
        question: GrantQuestion,
        limit: Optional[int] = None
    ) -> list[dict]:
        """Get relevant context for answering a specific question
        
        Args:
            entity_id: ID of the entity
            question: The grant question to find context for
            limit: Optional override for max sections to return
            
        Returns:
            list of relevant sections with their content and metadata
        """
        limit = limit or self.search_config.max_sections
        relevant_titles = self._get_relevant_section_titles(question)
        
        # Create enhanced search text combining question metadata
        search_text = f"""
        Category: {question.category}
        Title: {question.title}
        Question: {question.question}
        Answer Structure: {question.answer_structure_instructions}
        Content Guidelines: {question.answer_content_instructions}
        """
        
        # Generate embedding for the enhanced search text
        question_embedding = next(self.embedder.embed([search_text])).tolist()
        
        # Build hybrid search query
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=qdrant_models.QueryRequest(
                vector=question_embedding,
                filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="entity_id",
                            match=qdrant_models.MatchValue(value=entity_id)
                        ),
                        qdrant_models.FieldCondition(
                            key="title",
                            match=qdrant_models.MatchAny(any=relevant_titles)
                        )
                    ]
                ),
                with_payload=True,
                with_vectors=True,
                limit=limit,
                score_threshold=self.search_config.min_relevance_score
            )
        )
        
        # Extract and format relevant sections
        relevant_sections = []
        for point in search_result:
            section = {
                "title": point.payload["title"],
                "content": point.payload["summary"],
                "notes": point.payload["notes"],
                "analysis": point.payload["analysis"],
                "actionable_gap_analysis": point.payload["actionable_gap_analysis"],
                "score": point.score,
                "vector": point.vector  # Include vector for potential re-ranking
            }
            relevant_sections.append(section)
        
        return relevant_sections

    def get_all_sections(self, entity_id: str) -> list[dict]:
        """Get all sections for an entity
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            list of all sections with their content and metadata
        """
        search_result = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="entity_id",
                        match=qdrant_models.MatchValue(value=entity_id)
                    )
                ]
            ),
            with_payload=True,
            with_vectors=True,
            limit=100
        )[0]
        
        sections = []
        for point in search_result:
            section = {
                "title": point.payload["title"],
                "content": point.payload["summary"],
                "notes": point.payload["notes"],
                "analysis": point.payload["analysis"],
                "actionable_gap_analysis": point.payload["actionable_gap_analysis"],
                "vector": point.vector
            }
            sections.append(section)
        
        return sections 