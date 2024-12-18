from typing import Dict, Optional
import json
from src.utils.models import (
    Grant, 
    GrantQuestion, 
    GrantAnswer, 
    GrantResponse, 
    GrantInformation
)
from src.grant_answering.prompts import PromptBuilder
from src.utils.llm_client import LLMClient
from src.grant_answering.innovator_profile_provider import InnovatorProfileProvider

class GrantAnswering:
    """
    Grant answering workflow
    
    This class is responsible for answering grant questions using the LLM client and prompt builder.
    
    Usage:
    ```python
    llm_client = LLMClient(api_key="your_api_key")
    profile_provider = InnovatorProfileProvider(profile_data)
    grant_answering = GrantAnswering(llm_client, profile_provider)
    grant_response = grant_answering.process_grant_application(grant)
    ```
    """
    # Question types that require external input/processing
    EXTERNAL_SOURCE_TYPES = {
        "document",
    }
    
    def __init__(self, llm_client: LLMClient, profile_provider: InnovatorProfileProvider):
        """
        Initialize workflow with LLM client and profile provider
        
        Args:
            llm_client: Configured LLM client for generating responses
            profile_provider: Provider for innovator profile information
        """
        self._prompt_builder = PromptBuilder()
        self._llm_client = llm_client
        self._profile_provider = profile_provider
    
    def _get_relevant_fields(
        self, 
        grant_information: GrantInformation, 
        question: GrantQuestion
    ) -> Dict[str, str]:
        """Get relevant fields for the question using LLM."""
        relevance_prompt = self._prompt_builder.build_relevance_prompt(
            grant_information, 
            question
        )
        
        try:
            # Get LLM response
            relevance_response = self._llm_client.complete(relevance_prompt)
            
            # Extract JSON from response
            json_str = relevance_response.split("```json")[1].split("```")[0]
            relevant_fields = json.loads(json_str)["relevant_fields"]
            return relevant_fields
            
        except (IndexError, json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing relevance response for question {question.identifier}: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error getting relevant fields: {e}")
            return {}

    def _generate_answer(
        self, 
        grant_information: GrantInformation, 
        question: GrantQuestion, 
        relevant_fields: Dict[str, str]
    ) -> Optional[str]:
        """Generate answer for the question using LLM."""
        if question.type in self.EXTERNAL_SOURCE_TYPES:
            return None
        
        # Get innovator profile information
        innovator_profile = self._profile_provider.get_profile_info(question)
            
        answer_prompt = self._prompt_builder.build_answer_prompt(
            grant_information,
            question,
            relevant_fields,
            innovator_profile
        )
        
        try:
            # Get LLM response
            answer_response = self._llm_client.complete(answer_prompt)
            
            # Extract markdown content
            markdown_answer = answer_response.split("```markdown")[1].split("```")[0].strip()
            return markdown_answer
            
        except IndexError:
            print(f"Error extracting markdown from answer response for question {question.identifier}")
            return None
        except Exception as e:
            print(f"Unexpected error generating answer: {e}")
            return None

    def process_grant_application(
        self,
        grant: Grant
    ) -> GrantResponse:
        """
        Process all questions in the grant application.
        
        Args:
            grant: The grant application containing information and questions
            
        Returns:
            GrantResponse containing answers to all questions
        """
        answers = []
        
        for question in grant.questions:
            try:
                # Get relevant fields for the question
                relevant_fields = self._get_relevant_fields(grant.information, question)
                
                # Generate answer
                answer_text = self._generate_answer(
                    grant.information,
                    question,
                    relevant_fields
                )
                
                # Create GrantAnswer object
                answer = GrantAnswer(
                    identifier=question.identifier,
                    category=question.category,
                    title=question.title,
                    answer=answer_text
                )
                
                answers.append(answer)
                
            except Exception as e:
                print(f"Error processing question {question.identifier}: {e}")
                # Add error answer
                answer = GrantAnswer(
                    identifier=question.identifier,
                    category=question.category,
                    title=question.title,
                    answer="Error processing question"
                )
                answers.append(answer)
        
        return GrantResponse(answers=answers)
