"""Base classes for storage providers"""

from abc import ABC, abstractmethod
from typing import Optional

class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    def upload_file(self, file_path: str) -> str:
        """Upload a file to cloud storage
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            str: Public URL of the uploaded file
        """
        pass
    
    @abstractmethod
    def get_file_url(self, file_key: str) -> str:
        """Get the public URL for a file
        
        Args:
            file_key: Key/path of the file in storage
            
        Returns:
            str: Public URL of the file
        """
        pass 