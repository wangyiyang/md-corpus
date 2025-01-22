"""
md-corpus - A Python package for integrating Markdown files with cloud object storage
"""

from typing import Union, List
from pathlib import Path
import re
import mdformat

from .providers.base import StorageProvider
from .exceptions import MDCorpusError

class MDCorpus:
    """Main class for handling Markdown file conversions"""
    
    def __init__(self, provider: StorageProvider):
        """Initialize MDCorpus with a storage provider
        
        Args:
            provider: An instance of StorageProvider for handling cloud storage operations
        """
        self.provider = provider
        self.storage = provider  # For backward compatibility with tests
        
    def convert_file(self, file_path: Union[str, Path]) -> str:
        """Convert local resource links in a single Markdown file to cloud storage URLs
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            str: The converted Markdown content
            
        Raises:
            MDCorpusError: If file operations fail
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise MDCorpusError(f"File not found: {file_path}")
            
        try:
            # First format the file
            self.format_file(file_path)
            
            # Then convert image links
            content = file_path.read_text(encoding='utf-8')
            converted = self._process_content(content, file_path.parent)
            file_path.write_text(converted, encoding='utf-8')
            return converted
        except Exception as e:
            raise MDCorpusError(f"Failed to process file {file_path}: {str(e)}")
    
    def convert_directory(self, dir_path: Union[str, Path]) -> List[str]:
        """Convert local resource links in all Markdown files in a directory
        
        Args:
            dir_path: Path to the directory containing Markdown files
            
        Returns:
            List[str]: List of processed file paths
            
        Raises:
            MDCorpusError: If directory operations fail
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise MDCorpusError(f"Directory not found: {dir_path}")
            
        processed_files = []
        try:
            for md_file in dir_path.glob("**/*.md"):
                self.convert_file(md_file)
                processed_files.append(str(md_file))
            return processed_files
        except Exception as e:
            raise MDCorpusError(f"Failed to process directory {dir_path}: {str(e)}")

    def format_file(self, file_path: Union[str, Path]) -> str:
        """Format a single Markdown file
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            str: The formatted Markdown content
            
        Raises:
            MDCorpusError: If file operations fail
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise MDCorpusError(f"File not found: {file_path}")
            
        try:
            content = file_path.read_text(encoding='utf-8')
            formatted = mdformat.text(content)
            file_path.write_text(formatted, encoding='utf-8')
            return formatted
        except Exception as e:
            raise MDCorpusError(f"Failed to format file {file_path}: {str(e)}")
    
    def format_directory(self, dir_path: Union[str, Path]) -> List[str]:
        """Format all Markdown files in a directory
        
        Args:
            dir_path: Path to the directory containing Markdown files
            
        Returns:
            List[str]: List of processed file paths
            
        Raises:
            MDCorpusError: If directory operations fail
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise MDCorpusError(f"Directory not found: {dir_path}")
            
        processed_files = []
        try:
            for md_file in dir_path.glob("**/*.md"):
                self.format_file(md_file)
                processed_files.append(str(md_file))
            return processed_files
        except Exception as e:
            raise MDCorpusError(f"Failed to format directory {dir_path}: {str(e)}")
    
    def _process_content(self, content: str, base_path: Path) -> str:
        """Process Markdown content and convert local resource links
        
        Args:
            content: Markdown content to process
            base_path: Base path for resolving relative links
            
        Returns:
            str: Processed content with cloud storage URLs
        """
        # Match Markdown image and link syntax
        pattern = r'(!?\[.*?\]\()([^http].*?)(\))'
        
        def replace_match(match):
            prefix, path, suffix = match.groups()
            if path.startswith(('http://', 'https://', '#')): # Skip if already a URL
                return match.group(0)
                
            # Resolve and upload the resource
            resource_path = base_path / path.strip()
            if not resource_path.exists():
                return match.group(0)
                
            try:
                cloud_url = self.provider.upload_file(str(resource_path))
                # Handle HTML img tags
                if '<img' in prefix:
                    return f'{prefix}{cloud_url}{suffix}'
                # Handle Markdown image links with URL encoding
                return f'{prefix}{cloud_url}{suffix}'
            except Exception:
                return match.group(0)
        
        # Process Markdown image links
        content = re.sub(pattern, replace_match, content)
        
        # Process HTML img tags
        html_pattern = r'(<img\s+[^>]*src=")([^"]+)(")'
        content = re.sub(html_pattern, replace_match, content)
        
        return content

__version__ = "0.1.0" 