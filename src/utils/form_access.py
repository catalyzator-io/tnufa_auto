from typing import Protocol, Any, Optional

from src.utils.configs import FirebaseConfig

class FormStorageProvider(Protocol):
    """Protocol for accessing form storage (e.g. Firebase Storage)"""
    def download_file(self, path: str) -> bytes:
        """Download file contents from storage"""
        ...
    
    def get_file_from_url(self, url: str) -> bytes:
        """Download file contents from URL"""
        ...

class FormDatabaseProvider(Protocol):
    """Protocol for accessing form database (e.g. Firestore)"""
    def get_entity(self, entity_id: str) -> dict[str, Any]:
        """Get entity information"""
        ...
    
    def get_user(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get user information"""
        ...
    
    def get_form_submissions(self, entity_id: str, form_id: str) -> list[dict[str, Any]]:
        """Get form submissions"""
        ...

class FirebaseFormProvider:
    """Firebase implementation of form storage and database access"""
    def __init__(self, config: FirebaseConfig):
        import firebase_admin
        from firebase_admin import credentials, firestore, storage
        import requests
        
        cred = credentials.Certificate(config.credentials_path.as_posix())
        firebase_admin.initialize_app(cred, {
            'storageBucket': config.storage_bucket
        })
        self.db = firestore.client()
        self.bucket = storage.bucket()
        self.requests = requests
    
    def download_file(self, path: str) -> bytes:
        blob = self.bucket.blob(path)
        return blob.download_as_bytes()
    
    def get_file_from_url(self, url: str) -> bytes:
        response = self.requests.get(url)
        response.raise_for_status()
        return response.content
    
    def get_entity(self, entity_id: str) -> dict[str, Any]:
        entity_doc = self.db.collection('entities').document(entity_id).get()
        if not entity_doc.exists:
            raise ValueError(f"Entity {entity_id} not found")
        return entity_doc.to_dict()
    
    def get_user(self, user_id: str) -> Optional[dict[str, Any]]:
        user_doc = self.db.collection('users').document(user_id).get()
        return user_doc.to_dict() if user_doc.exists else None
    
    def get_form_submissions(self, entity_id: str, form_id: str) -> list[dict[str, Any]]:
        submissions_ref = (self.db
            .collection('entities')
            .document(entity_id)
            .collection('forms')
            .document(form_id)
            .collection('submissions')
        )
        return [{**sub.to_dict(), 'id': sub.id} for sub in submissions_ref.stream()] 