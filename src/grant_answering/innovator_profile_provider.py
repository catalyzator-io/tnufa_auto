from typing import Optional, get_args
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from fastembed import TextEmbedding
from pydantic import BaseModel, Field
from src.utils.taxonomy import taxonomy, section_info
from src.utils.models import GrantQuestion, SectionTitle
from src.utils.configs import QdrantConfig
from src.utils.llm_client import LLMClient

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
        llm_client: LLMClient = None,
        qdrant_config: Optional[QdrantConfig] = None,
        search_config: Optional[SearchConfig] = None,
    ):
        self.collection_name = collection_name
        self.qdrant_config = qdrant_config or QdrantConfig()
        self.search_config = search_config or SearchConfig()
        self.client = QdrantClient(**self.qdrant_config.model_dump())
        self.embedder = TextEmbedding('sentence-transformers/all-MiniLM-L6-v2')
        
        if llm_client is None:
            raise ValueError("LLM client is required")
        
        self.llm_client = llm_client
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
            "DEVELOPMENT_EXECUTION": ["Development and Execution"],
            "LEGAL_COMPLIANCE": ["Legal and Compliance"],
            "IMPACT_INNOVATION": ["Impact and Innovation"]
        }
        return mapping

    async def _get_relevant_section_titles_llm(self, question: GrantQuestion) -> list[str]:
        """Get relevant section titles using LLM prompting
        
        Args:
            question: The grant question to find relevant sections for
            
        Returns:
            list of relevant section titles
        """
        # Build prompt for LLM
        prompt = f"""Given the following grant question details:
        Category: {question.category}
        Title: {question.title}
        Question: {question.question}
        Answer Structure: {question.answer_structure_instructions}
        Content Guidelines: {question.answer_content_instructions}

        And these available sections:
        {[title.value for title in get_args(SectionTitle)]}

        Return only the most relevant section titles as a comma-separated list.
        Consider the question's topic, requirements, and what information would be needed to provide a comprehensive answer.
        """

        response = await self.llm_client.acompletion(prompt)
        # Parse comma-separated response into list
        suggested_titles = [title.strip() for title in response.split(',')]
        
        # Validate titles against actual SectionTitle values
        valid_titles = [title for title in suggested_titles if title in get_args(SectionTitle)]
        return valid_titles

    def _get_relevant_section_titles_taxonomy(self, question: GrantQuestion) -> list[str]:
        """Get relevant section titles using taxonomy matching
        
        Args:
            question: The grant question to find relevant sections for
            
        Returns:
            list of relevant section titles
        """
        relevant_titles = set()
        
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
        
        return list(relevant_titles)

    def _get_relevant_sections_embedding(
        self,
        entity_id: str,
        question: GrantQuestion,
        limit: int
    ) -> list[dict]:
        """Get relevant sections using embedding-based similarity search
        
        Args:
            entity_id: ID of the entity
            question: The grant question
            limit: Maximum number of sections to return
            
        Returns:
            List of relevant sections with scores
        """
        search_text = f"""
        Category: {question.category}
        Title: {question.title}
        Question: {question.question}
        Answer Structure: {question.answer_structure_instructions}
        Content Guidelines: {question.answer_content_instructions}
        """
        
        question_embedding = next(self.embedder.embed([search_text])).tolist()
        
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=qdrant_models.QueryRequest(
                vector=question_embedding,
                filter=qdrant_models.FieldCondition(
                    key="entity_id",
                    match=qdrant_models.MatchValue(value=entity_id)
                ),
                with_payload=True,
                with_vectors=True,
                limit=limit,
                score_threshold=self.search_config.min_relevance_score
            )
        )
        
        return [self._format_section(point) for point in search_result]

    async def get_relevant_context(
        self,
        entity_id: str,
        question: GrantQuestion,
        limit: Optional[int] = None
    ) -> list[dict]:
        """Get relevant context using hybrid search combining LLM and embedding approaches
        
        Args:
            entity_id: ID of the entity
            question: The grant question to find context for
            limit: Optional override for max sections to return
            
        Returns:
            list of relevant sections with their content and metadata
        """
        limit = limit or self.search_config.max_sections
        
        # Get relevant sections using both approaches
        taxonomy_titles = self._get_relevant_section_titles_taxonomy(question)
        llm_titles = await self._get_relevant_section_titles_llm(question)
        embedding_results = self._get_relevant_sections_embedding(entity_id, question, limit)
        
        # Combine unique titles from both approaches
        relevant_titles = list(set(taxonomy_titles + llm_titles))
        
        # Filter embedding results by relevant titles
        filtered_results = [
            section for section in embedding_results 
            if section["title"] in relevant_titles
        ]
        
        # If we don't have enough results, get additional sections from relevant titles
        if len(filtered_results) < limit:
            additional_results = self.client.query_points(
                collection_name=self.collection_name,
                query=qdrant_models.QueryRequest(
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
                    limit=limit - len(filtered_results)
                )
            )
            filtered_results.extend(self._format_section(point) for point in additional_results)
        
        return filtered_results[:limit]

    def _format_section(self, point) -> dict:
        """Helper method to format a search result point into a section dict"""
        return {
            "title": point.payload["title"],
            "content": point.payload["summary"],
            "notes": point.payload["notes"],
            "analysis": point.payload["analysis"],
            "actionable_gap_analysis": point.payload["actionable_gap_analysis"],
            "score": getattr(point, 'score', None),
            "vector": point.vector
        }

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