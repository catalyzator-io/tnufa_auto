from typing import get_args
from fastembed import TextEmbedding
from src.utils.models import (
    GrantQuestion, SectionTitle, ProfileSection,
    SearchResult, QdrantPoint
)
from src.utils.configs import SearchConfig
from src.utils.llm_client import LLMClient
from src.utils.qdrant_access import QdrantAccess, QdrantFilter

class InnovatorProfileProvider:
    """Provides relevant innovator profile information for answering grant questions"""
    
    def __init__(
        self,
        collection_name: str,
        llm_client: LLMClient,
        qdrant: QdrantAccess,
        filter_builder: QdrantFilter,
        search_config: SearchConfig,
    ):
        self.collection_name = collection_name
        self.search_config = search_config
        self.qdrant = qdrant
        self.filter_builder = filter_builder
        self.llm_client = llm_client
        self.embedder = TextEmbedding(self.search_config.embedding_config.model_name)

    def _point_to_section(self, point: QdrantPoint) -> ProfileSection:
        """Convert QdrantPoint to ProfileSection"""
        return ProfileSection(
            title=point.payload["title"],
            summary=point.payload["summary"],
            notes=point.payload["notes"],
            analysis=point.payload["analysis"],
            actionable_gap_analysis=point.payload["actionable_gap_analysis"],
            vector=point.vector,
            score=point.score
        )

    def _get_relevant_sections_llm(
        self,
        entity_id: str,
        question: GrantQuestion
    ) -> list[ProfileSection]:
        """Get relevant sections using LLM prompting"""
        # Build prompt for LLM
        prompt = f"""
        You are an expert grant writing consultant with extensive experience in matching grant questions with relevant supporting information. Your task is to analyze a grant question and identify the most relevant sections that would provide comprehensive supporting evidence.

        CONTEXT:
        You are helping identify which sections of an innovator's profile would best support answering a specific grant question.

        INPUT DETAILS:
        Grant Question Category: {question.category}
        Question Title: {question.title}
        Question Text: {question.question}
        Answer Structure Requirements: {question.answer_structure_instructions}
        Content Guidelines: {question.answer_content_instructions}

        Available Profile Sections:
        {[title.value for title in get_args(SectionTitle)]}

        TASK:
        1. Analyze the grant question requirements and content guidelines
        2. Review the available profile sections
        3. Select only the most relevant sections that would provide direct evidence or support for answering this specific question
        4. Order the sections by relevance (most relevant first)

        OUTPUT REQUIREMENTS:
        - Return ONLY a comma-separated list of section titles
        - Include no more than 5 most relevant sections
        - Do not include any explanation or additional text
        - Format example: "The Problem, The Solution, Market Analysis"
        """

        response = self.llm_client.complete(prompt)
        suggested_titles = [title.strip() for title in response.split(',')]
        valid_titles = [title for title in suggested_titles 
                       if title in get_args(SectionTitle)]

        # Fetch sections data for the valid titles
        filters = (
            self.filter_builder
                .add("entity_id", entity_id)
                .add_any("section_title", valid_titles)
        )
        
        points = self.qdrant.filter(
            collection=self.collection_name,
            filters=filters,
            limit=self.search_config.max_sections
        )
        
        return [self._point_to_section(point) for point in points]

    def _get_relevant_sections_embedding(
        self,
        entity_id: str,
        question: GrantQuestion
    ) -> list[ProfileSection]:
        """Get relevant sections using embedding-based similarity search"""
        search_text = f"""
        Category: {question.category}
        Title: {question.title}
        Question: {question.question}
        Answer Structure: {question.answer_structure_instructions}
        Content Guidelines: {question.answer_content_instructions}
        """
        
        query_vector = next(self.embedder.embed([search_text])).tolist()
        
        filters = self.qdrant.create_filter().add("entity_id", entity_id)
        points = self.qdrant.search(
            collection=self.collection_name,
            query_vector=query_vector,
            filters=filters,
            limit=self.search_config.max_sections,
            score_threshold=self.search_config.min_relevance_score
        )
        
        return [self._point_to_section(point) for point in points]

    def get_relevant_context(
        self,
        entity_id: str,
        question: GrantQuestion,
    ) -> SearchResult:
        """Get relevant context using hybrid search"""
        # Get relevant sections using both approaches
        llm_sections = self._get_relevant_sections_llm(entity_id, question)
        embedding_sections = self._get_relevant_sections_embedding(entity_id, question)
        
        # Combine results, removing duplicates based on content
        return SearchResult(
            sections=list(set(embedding_sections) & set(llm_sections))

        )
