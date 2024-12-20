from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


QuestionType = Literal["text", "table", "document", "number", "date", "boolean"]

class GrantQuestion(BaseModel):
    identifier: str = Field(..., description="The identifier of the question", example="5.2")
    type: QuestionType = Field(..., description="The type of the question", example="text")
    category: str = Field(..., description="The category of the question", example="5. Innovation")
    title: str = Field(..., description="The title of the question")
    question: str = Field(..., description="The text of the question")
    answer_structure_instructions: str = Field(..., description="The instructions for the structure of the answer")
    answer_content_instructions: str = Field(..., description="The instructions for the content of the answer and its formatting and sentiment")

class GrantAnswer(BaseModel):
    identifier: str = Field(..., description="The identifier of the question")
    category: str = Field(..., description="The category of the question")
    title: str = Field(..., description="The title of the question")
    answer: Optional[str] = Field(..., description="The answer to the question")

class GrantInformation(BaseModel):
    track_name: str = Field(..., description="Name of the grant track (e.g., 'Tnufa')")
    description: str = Field(..., description="General description of the track")
    purpose: str = Field(..., description="The main purpose/goal of the grant track")
    target_audience: str = Field(..., description="Description of who is eligible for the grant")
    grant_amount: dict = Field(..., description="Details about the grant amount", example={
        "percentage": 80,
        "maximum_amount": 200000,
        "currency": "NIS",
        "duration_months": 12,
        "maximum_budget": 250000
    })
    eligible_expenses: list[str] = Field(..., description="List of expenses that can be covered by the grant")
    benefits: list[str] = Field(..., description="Key benefits of the grant program")
    eligibility_conditions: list[str] = Field(..., description="List of conditions that must be met to be eligible")
    company_requirements: dict = Field(..., description="Specific requirements for companies", example={
        "max_annual_income": 200000,
        "max_funding_raised": 500000,
        "currency": "NIS"
    })
    obligations: list[str] = Field(..., description="Legal and regulatory obligations for grant recipients")
    royalty_terms: dict = Field(..., description="Terms for royalty payments", example={
        "percentage": 3,
        "trigger": "commercialization and sales"
    })
    evaluation_criteria: list[str] = Field(..., description="Criteria used to evaluate grant applications")


class Grant(BaseModel):
    information: GrantInformation
    questions: list[GrantQuestion]


class GrantResponse(BaseModel):
    answers: list[GrantAnswer]


TaxonomyCategory = Literal[
    "TEAM_LEADERSHIP",
    "COMPANY_FUNDAMENTALS",
    "PRODUCT_TECHNOLOGY",
    "MARKET_ANALYSIS",
    "BUSINESS_MODEL",
    "TRACTION_VALIDATION",
    "FINANCIAL_INFORMATION",
    "DEVELOPMENT_EXECUTION",
    "LEGAL_COMPLIANCE",
    "IMPACT_INNOVATION"
]

Taxonomy = dict[TaxonomyCategory, list[str]]

SectionTitle = Literal[
    "Introduction",
    "The Problem",
    "The Need",
    "The Solution",
    "The Business Model",
    "Go-to-Market Strategy",
    "Market Opportunity",
    "Technology/Innovation",
    "Competitive Analysis",
    "Traction and Validation",
    "Team and Leadership",
    "Financial Information",
    "Development and Execution",
    "Legal and Compliance",
    "Impact and Innovation",
    "Additional Supporting Information",
    "Others"
]

SectionInfo = dict[SectionTitle, str]

class EnhancedContentSection(BaseModel):
    title: SectionTitle
    summary: str
    notes: str
    analysis: str
    actionable_gap_analysis: str
    
    def to_string(self) -> str:
        return f"### {self.title}\n**Summary:**\n{self.summary}\n**Notes:**\n{self.notes}\n**Analysis:**\n{self.analysis}\n"


class EnhancedContent(BaseModel):
    basic_info: dict[str, Any]
    sections: list[EnhancedContentSection]

class QdrantPoint(BaseModel):
    """Represents a point in Qdrant with its payload and vector"""
    payload: dict[str, Any]
    vector: list[float]
    score: Optional[float] = None

class ProfileSection(EnhancedContentSection):
    """Represents a section of an innovator's profile"""
    vector: list[float]
    score: Optional[float] = None

class SearchResult(BaseModel):
    """Represents search results for profile sections"""
    sections: list[ProfileSection]
    
    def to_string(self) -> str:
        return "\n".join([section.to_string() for section in self.sections])
