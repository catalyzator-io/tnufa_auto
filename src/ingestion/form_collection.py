from typing import Any, Optional, Iterator
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, storage
import requests

from src.ingestion.extract import ContentExtractorProtocol

class FormCollector:
    """Collects and processes form submissions and related files from Firebase"""
    
    def __init__(
        self, 
        firebase_config_path: Path, 
        content_extractor: ContentExtractorProtocol,
        form_id: str = 'innovator_introduction'
    ):
        """Initialize Firebase connection and set form type
        
        Args:
            firebase_config_path: Path to Firebase credentials file
            content_extractor: Configured ContentExtractor instance
            form_id: Form identifier to collect (defaults to innovator_introduction)
        """
        cred = credentials.Certificate(firebase_config_path.as_posix())
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'catalyzator.appspot.com'
        })
        self.db = firestore.client()
        self.bucket = storage.bucket()
        self.form_id = form_id
        self.content_extractor = content_extractor

    def _find_file_data(self, data: Any) -> Iterator[dict[str, Any]]:
        """Recursively find all file data in a nested structure
        
        Args:
            data: Any data structure that might contain file information
            
        Yields:
            dictionaries containing file information
        """
        if isinstance(data, dict):
            if any(key in data for key in ['url', 'filename', 'path', 'relativePath']):
                yield data
            else:
                for value in data.values():
                    yield from self._find_file_data(value)
        elif isinstance(data, list):
            for item in data:
                yield from self._find_file_data(item)

    def _get_entity_info(self, entity_id: str) -> dict[str, Any]:
        """Get entity information including member details"""
        entity_doc = self.db.collection('entities').document(entity_id).get()
        if not entity_doc.exists:
            raise ValueError(f"Entity {entity_id} not found")
        
        entity_data = entity_doc.to_dict()
        
        # Get detailed member information
        members_data = []
        for member_id in entity_data.get('members', []):
            member_doc = self.db.collection('users').document(member_id).get()
            if member_doc.exists:
                members_data.append(member_doc.to_dict())
        
        entity_data['members'] = members_data
        return entity_data

    def _download_and_process_file(self, file_data: dict[str, Any]) -> Optional[str]:
        """Download and extract text from a file using either URL or Firebase Storage path
        
        Args:
            file_data: Dictionary containing file information (url, path, relativePath, filename)
            
        Returns:
            Extracted text content from the file, or None if processing fails
        """
        try:
            # Case 1: Direct URL available
            if file_data.get('url'):
                response = requests.get(file_data['url'])
                response.raise_for_status()
                return self.content_extractor.extract_text(response.content, file_data['filename'])
            
            # Case 2: Firebase Storage path available
            storage_path = file_data.get('path') or file_data.get('relativePath')
            if storage_path:
                # Get a reference to the file in Firebase Storage
                blob = self.bucket.blob(storage_path)
                
                # Download the file contents to memory
                file_contents = blob.download_as_bytes()
                
                return self.content_extractor.extract_text(file_contents, file_data.get('filename', Path(storage_path).name))
            
            return None
            
        except Exception as e:
            print(f"Error processing file {file_data.get('filename')}: {e}")
            return None

    def collect_form_data(self, entity_id: str) -> dict[str, Any]:
        """Collect form data, entity information, and file contents for an entity
        
        Args:
            entity_id: Entity identifier to collect data for
            
        Returns:
            dictionary containing entity info, form data, and file contents
        """
        # Get entity information
        entity_info = self._get_entity_info(entity_id)
        
        # Get form submissions
        submissions_ref = (self.db
            .collection('entities')
            .document(entity_id)
            .collection('forms')
            .document(self.form_id)
            .collection('submissions')
        )
        
        form_data = []
        file_contents = {}
        
        for submission in submissions_ref.stream():
            submission_data = submission.to_dict()
            submission_data['id'] = submission.id
            
            # Find and process all files in the submission data
            for file_data in self._find_file_data(submission_data):
                content = self._download_and_process_file(file_data)
                if content:
                    file_contents[file_data['filename']] = content
                    file_data['content_ref'] = file_data['filename']
            
            form_data.append(submission_data)
        
        return {
            'entity': entity_info,
            'form_data': form_data,
            'file_contents': file_contents
        }
