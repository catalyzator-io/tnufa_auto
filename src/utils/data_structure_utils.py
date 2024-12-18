from typing import Any, Iterator

_file_keys = ['url', 'filename', 'path', 'relativePath']

def find_file_data(data: Any) -> Iterator[dict[str, Any]]:
    """Recursively find all file data in a nested structure
    
    Args:
        data: Any data structure that might contain file information
        
    Yields:
        dictionaries containing file information
    """
    if isinstance(data, dict):
        if any(key in data for key in _file_keys):
            yield data
        else:
            for value in data.values():
                yield from find_file_data(value)
    elif isinstance(data, list):
        for item in data:
            yield from find_file_data(item)

def remove_file_data(data: Any) -> Any:
    """Recursively remove file-related data from a nested structure
    
    Args:
        data: Any data structure that might contain file information
        
    Returns:
        Cleaned data structure with file information removed
    """
    if isinstance(data, dict):
        if any(file_key in data for file_key in _file_keys):
            return None
        cleaned = {}
        for key, value in data.items():
            cleaned_value = remove_file_data(value)
            if cleaned_value:
                cleaned[key] = cleaned_value
        
        return cleaned or None
        
    elif isinstance(data, list):
        cleaned = [
            item for item in (remove_file_data(x) for x in data)
            if item is not None
        ]
        return cleaned or None
        
    return data 