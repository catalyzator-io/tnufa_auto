from typing import Optional, Protocol, Dict
from pathlib import Path
import re

class ContentExtractorProtocol(Protocol):
    """Protocol for content extractors"""
    def extract_text(self, file_data: bytes, filename: str) -> Optional[str]:
        """Extract text content from supported file types
        
        Args:
            file_data: Raw bytes of the file
            filename: Name of the file including extension
            
        Returns:
            Extracted text if successful, None otherwise
        """
        ...

class BaseExtractor(ContentExtractorProtocol):
    """Base class for all extractors"""
    
    supported_formats: set[str] = set()
    
    def extract_text(self, file_data: bytes, filename: str) -> Optional[str]:
        """Default implementation that should be overridden"""
        raise NotImplementedError()
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and normalizing line endings"""
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return "\n".join(line.strip() for line in text.splitlines()).strip()
    
    @classmethod
    def supports_format(cls, filename: str) -> bool:
        """Check if this extractor supports the given file format"""
        return Path(filename).suffix.lower() in cls.supported_formats

class ContentExtractor:
    """Main coordinator for content extraction"""
    
    def __init__(self):
        """Initialize with default extractors"""
        self._extractors: Dict[str, BaseExtractor] = {}
        
    def register_extractor(self, name: str, extractor: BaseExtractor) -> None:
        """Register a new extractor
        
        Args:
            name: Unique name for the extractor
            extractor: Extractor instance
        """
        self._extractors[name] = extractor
    
    def extract_text(self, file_data: bytes, filename: str) -> Optional[str]:
        """Extract text using the appropriate extractor
        
        Args:
            file_data: Raw bytes of the file
            filename: Name of the file including extension
            
        Returns:
            Extracted text if successful, None otherwise
            
        Raises:
            ValueError: If no suitable extractor is found
        """
        for extractor in self._extractors.values():
            if extractor.supports_format(filename):
                try:
                    return extractor.extract_text(file_data, filename)
                except Exception as e:
                    print(f"Error extracting text with {type(extractor).__name__}: {e}")
                    continue
        
        raise ValueError(f"No suitable extractor found for {filename}") 