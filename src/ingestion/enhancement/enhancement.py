from typing import Protocol
from src.utils.models import EnhancedContent
from src.utils.llm_client import LLMClient
from src.ingestion.enhancement.prompt import get_prompt, extract_sections
from src.utils.data_structure_utils import remove_file_data

class ContentEnhancerProtocol(Protocol):
    """Protocol for content enhancement implementations"""
    def process_content(self, content: dict) -> EnhancedContent:
        """Process and enhance raw content"""
        ...

class ContentEnhancer(ContentEnhancerProtocol):
    """Main content enhancement coordinator"""
    
    def __init__(self, llm: LLMClient):
        self._llm_client = llm
    
    def _get_basic_info(self, content: dict) -> dict:
        """Extract basic information from form data with file data removed"""
        form_data: dict = content['form_data'][0]['data']
        cleaned_data: dict = remove_file_data(form_data)
        return cleaned_data or {}
    
    def process_content(self, content: dict) -> EnhancedContent:
        """Process and enhance raw content"""
        basic_info = self._get_basic_info(content)

        prompt = get_prompt(content['file_contents'])
        sections = extract_sections(self._llm_client.complete(prompt))
        return EnhancedContent(basic_info=basic_info, sections=sections)
