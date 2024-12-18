from typing import Dict
from src.utils.models import GrantInformation, GrantQuestion

class PromptBuilder:
    _system_context = """You are an expert grant consultant with years of experience in helping innovators secure funding. 
Your role is to provide strategic, compelling, and well-crafted responses that highlight the alignment between the innovator's strengths and the grant's objectives."""

    def build_relevance_prompt(
        self,
        grant_info: GrantInformation,
        question: GrantQuestion
    ) -> str:
        """
        Builds a prompt to determine which parts of the grant information are most relevant
        for answering a specific question and to provide a reason for each field.
        """
        prompt_parts = [
            self._system_context,
            "\nAnalyze this grant question strategically. Identify the key grant information fields that would help craft "
            "a compelling and competitive response. For each relevant field, explain how it can be leveraged to strengthen the application.",
            "\nQuestion Context:",
            f"Category: {question.category}",
            f"Type: {question.type}",
            f"Question: {question.question}",
            "\nAvailable Grant Information Fields:",
        ]

        # Add all available fields from GrantInformation with their descriptions
        for field, field_info in grant_info.model_fields.items():
            prompt_parts.append(f"- {field.replace('_', ' ').title()}: {field_info.description}")

        prompt_parts.extend([
            "\nProvide your response in the following format:",
            "```json",
            '{',
            '    "relevant_fields": {',
            '        "field_name": "reason for relevance",',
            '        ...',
            '    }',
            '}',
            '```',
            "\nInclude only the fields that are directly relevant to answering this specific question."
        ])

        return "\n".join(prompt_parts)

    def build_answer_prompt(
        self,
        grant_info: GrantInformation,
        question: GrantQuestion,
        relevant_fields: Dict[str, str],
        innovator_profile: str
    ) -> str:
        """
        Builds the complete prompt for generating an answer to a specific grant question.
        
        Args:
            grant_info: The complete grant information
            question: The question to be answered
            relevant_fields: Dictionary of field names and their relevance explanations
            innovator_profile: Profile information about the innovator
        """
        # Extract only the relevant information from grant_info
        relevant_info = {
            field: getattr(grant_info, field)
            for field in relevant_fields.keys()
            if hasattr(grant_info, field)
        }

        prompt_parts = [
            self._system_context,
        ]

        if relevant_info:
            prompt_parts.append("\nRelevant Grant Information:")
            for field, value in relevant_info.items():
                reason = relevant_fields[field]
                prompt_parts.extend([
                    f"{field.replace('_', ' ').title()}: {value}",
                    f"(Relevant because: {reason})"
                ])

        # Add question details
        prompt_parts.extend([
            "\nQuestion Details:",
            f"Category: {question.category}",
            f"Type: {question.type}",
            f"Question: {question.question}"
        ])

        # Enhanced answer instructions
        prompt_parts.extend([
            "\nResponse Strategy:",
            (
                "Structure: "
                f"{question.answer_structure_instructions} "
                "Craft your response in a clear, professional markdown format that emphasizes key points "
                "and maintains a confident, authoritative tone throughout."
            ),
            (
                "Content Approach: "
                f"{question.answer_content_instructions} "
                "Your response should be compelling and strategic, demonstrating deep understanding of both "
                "the grant's objectives and the innovation's potential. Use concrete examples and specific details "
                "to build credibility. Maintain a professional yet engaging tone that conveys expertise and vision. "
                "Use only content from the innovator's profile. Do not use any other information. "
                "Be focused on the question and the grant information. Provide a focused answer to the question. "
            ),
            (
                "Strategic Focus: "
                "- Align the innovator's profile with the grant's objectives and evaluation criteria\n"
                "- Emphasize unique strengths and competitive advantages\n"
                "- Demonstrate clear understanding of the grant's purpose and requirements\n"
                "- Address potential concerns proactively\n"
                "- Use specific, quantifiable details where possible\n"
                "- Maintain a confident yet grounded tone\n"
                "- Show forward-thinking vision while remaining practical"
            ),
            (
                "Key Principles:\n"
                "1. Be specific and substantive - avoid generic statements\n"
                "2. Show don't tell - use concrete examples\n"
                "3. Demonstrate strategic thinking and long-term vision\n"
                "4. Address evaluation criteria both explicitly and implicitly\n"
                "5. Maintain professional enthusiasm and confidence\n"
                "6. Focus on value creation and impact"
            )
        ])

        prompt_parts.extend([
            "\nInnovator Context:",
            innovator_profile,
            "\nCrafting Guidelines:",
            "- Write in a clear, professional tone that builds credibility",
            "- Use specific examples and metrics where possible",
            "- Demonstrate strategic thinking and vision",
            "- Show clear alignment with grant objectives",
            "- Maintain confidence while being realistic",
            "- Focus on unique value proposition and impact potential"
        ])

        prompt_parts.append(
            "\nImportant: Your response should read as if written by a seasoned professional "
            "with deep industry expertise. Avoid generic or overly formal language. "
            "Instead, craft a response that demonstrates strategic thinking, clear vision, "
            "and compelling potential. Start with ```markdown and end with ```."
        )
        
        prompt_parts.extend([
            "\nQuestion to Address:",
            f"{question.question}",
            "\nStrategic Response:"
        ])

        return "\n".join(prompt_parts)


# Usage example:
"""
prompt_builder = PromptBuilder()

# First step: Get relevance prompt to determine relevant fields
relevance_prompt = prompt_builder.build_relevance_prompt(grant_info, question)
# Use this prompt with LLM to get relevant_fields dictionary
# relevant_fields = llm_response_parsed_as_dict

# Second step: Build answer prompt using the relevant fields
answer_prompt = prompt_builder.build_answer_prompt(
    grant_info,
    question,
    relevant_fields,
    innovator_profile="The innovator is a software developer with 5 years of experience..."
)
"""
