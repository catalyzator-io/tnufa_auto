from typing import Protocol, Any
from src.utils.models import EnhancedContent
from src.utils.llm_client import LLMClient
from src.ingestion.enhancement.prompt import get_prompt, extract_sections

class ContentEnhancerProtocol(Protocol):
    """Protocol for content enhancement implementations"""
    def process_content(self, content: dict) -> EnhancedContent:
        """Process and enhance raw content"""
        ...

class ContentEnhancer(ContentEnhancerProtocol):
    """Main content enhancement coordinator"""
    
    def __init__(self, llm: LLMClient):
        self._llm_client = llm
    
    def _remove_file_data(self, data: Any) -> Any:
        """Recursively remove file-related data from a nested structure
        
        Args:
            data: Any data structure that might contain file information
            
        Returns:
            Cleaned data structure with file information removed
        """
        if isinstance(data, dict):
            if any(file_key in data for file_key in ['url', 'filename', 'path', 'relativePath']):
                return None
            cleaned = {}
            for key, value in data.items():
                cleaned_value = self._remove_file_data(value)
                if cleaned_value:
                    cleaned[key] = cleaned_value
            
            return cleaned or None
            
        elif isinstance(data, list):
            cleaned = [
                item for item in (self._remove_file_data(x) for x in data)
                if item is not None
            ]
            return cleaned or None
            
        return data
    
    def _get_basic_info(self, content: dict) -> dict:
        """Extract basic information from form data with file data removed"""
        form_data: dict = content['form_data']['data']
        cleaned_data: dict = self._remove_file_data(form_data)
        return cleaned_data or {}
    
    def process_content(self, content: dict) -> EnhancedContent:
        """Process and enhance raw content"""
        basic_info = self._get_basic_info(content)

        prompt = get_prompt(content['raw_data'])
        sections = extract_sections(self._llm_client.complete(prompt))
        return EnhancedContent(basic_info=basic_info, sections=sections)
