from typing import Any, Optional
from pathlib import Path

from src.ingestion.extract import ContentExtractorProtocol
from src.utils.data_structure_utils import find_file_data
from src.utils.form_access import FormStorageProvider, FormDatabaseProvider

class FormCollector:
    """Collects and processes form submissions and related files"""
    
    def __init__(
        self, 
        storage_provider: FormStorageProvider,
        database_provider: FormDatabaseProvider,
        content_extractor: ContentExtractorProtocol,
        form_id: str = 'innovator_introduction'
    ):
        """Initialize form collector with providers
        
        Args:
            storage_provider: Provider for file storage access
            database_provider: Provider for database access
            content_extractor: Configured ContentExtractor instance
            config: Firebase configuration
        """
        self.storage = storage_provider
        self.database = database_provider
        self.content_extractor = content_extractor
        self.form_id = form_id

    def _get_entity_info(self, entity_id: str) -> dict[str, Any]:
        """Get entity information including member details"""
        entity_data = self.database.get_entity(entity_id)
        
        # Get detailed member information
        members_data = []
        for member_id in entity_data.get('members', []):
            if member_data := self.database.get_user(member_id):
                members_data.append(member_data)
        
        entity_data['members'] = members_data
        return entity_data

    def _download_and_process_file(self, file_data: dict[str, Any]) -> Optional[str]:
        """Download and extract text from a file
        
        Args:
            file_data: Dictionary containing file information
            
        Returns:
            Extracted text content from the file, or None if processing fails
        """
        try:
            filename = file_data.get('filename', '')
            
            if url := file_data.get('url'):
                file_contents = self.storage.get_file_from_url(url)
            elif storage_path := (file_data.get('path') or file_data.get('relativePath')):
                file_contents = self.storage.download_file(storage_path)
                filename = filename or Path(storage_path).name
            else:
                return None
                
            return self.content_extractor.extract_text(file_contents, filename)
            
        except Exception as e:
            print(f"Error processing file {file_data.get('filename')}: {e}")
            return None

    def collect_form_data(self, entity_id: str) -> dict[str, Any]:
        """Collect form data, entity information, and file contents for an entity"""
        # Get entity information
        entity_info = self._get_entity_info(entity_id)
        
        # Get form submissions
        form_data = self.database.get_form_submissions(entity_id, self.form_id)
        file_contents = {}
        
        # Process files in submissions
        for submission in form_data:
            for file_data in find_file_data(submission):
                if content := self._download_and_process_file(file_data):
                    file_contents[file_data['filename']] = content
        
        return {
            'entity': entity_info,
            'form_data': form_data,
            'file_contents': file_contents
        }
