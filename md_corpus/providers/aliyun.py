"""Aliyun OSS storage provider implementation"""

import os
from pathlib import Path
import mimetypes
import oss2
from urllib.parse import quote

from .base import StorageProvider
from ..exceptions import MDCorpusError

class AliyunProvider(StorageProvider):
    """Aliyun OSS storage provider"""
    
    def __init__(
        self,
        bucket: str,
        access_key: str = None,
        secret_key: str = None,
        endpoint: str = None,
        internal: bool = False,
        cname: str = None
    ):
        """Initialize Aliyun OSS provider
        
        Args:
            bucket: OSS bucket name
            access_key: Aliyun access key ID (optional, can be set via ALI_OSS_ACCESS_KEY_ID env var)
            secret_key: Aliyun access key secret (optional, can be set via ALI_OSS_ACCESS_KEY_SECRET env var)
            endpoint: OSS endpoint (optional, can be set via ALI_OSS_ENDPOINT env var)
            internal: Whether to use internal endpoint
            cname: Custom domain name (CNAME) for the bucket
        """
        self.bucket_name = bucket
        self.internal = internal
        self.cname = cname
        
        # Get credentials from env vars if not provided
        access_key = access_key or os.getenv('ALI_OSS_ACCESS_KEY_ID')
        secret_key = secret_key or os.getenv('ALI_OSS_ACCESS_KEY_SECRET')
        endpoint = endpoint or os.getenv('ALI_OSS_ENDPOINT')
        
        if not endpoint:
            raise MDCorpusError("Missing required Aliyun OSS endpoint")
        if not access_key or not secret_key:
            raise MDCorpusError("Missing required Aliyun OSS credentials")
        
        # Use internal endpoint if specified
        if internal and not endpoint.startswith('oss-internal.'):
            endpoint = endpoint.replace('oss.', 'oss-internal.')
        
        # Initialize OSS auth and bucket
        auth = oss2.Auth(access_key, secret_key)
        self.bucket = oss2.Bucket(auth, endpoint, bucket)
    
    def upload_file(self, file_path: str) -> str:
        """Upload a file to OSS
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            str: Public URL of the uploaded file
            
        Raises:
            MDCorpusError: If upload fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise MDCorpusError(f"File not found: {file_path}")
        
        # Generate OSS key from file path
        key = str(file_path.name)
        
        # Detect content type
        content_type = mimetypes.guess_type(file_path)[0]
        headers = {'Content-Type': content_type} if content_type else {}
        
        try:
            with open(file_path, 'rb') as f:
                self.bucket.put_object(key, f, headers=headers)
                self.bucket.put_object_acl(key, 'public-read')
            return self.get_file_url(key)
        except oss2.exceptions.OssError as e:
            raise MDCorpusError(f"Failed to upload file to OSS: {str(e)}")
    
    def get_file_url(self, file_key: str) -> str:
        """Get the public URL for a file in OSS
        
        Args:
            file_key: Key of the file in OSS
            
        Returns:
            str: Public URL of the file
        """
        # URL encode the key
        encoded_key = quote(file_key)
        
        if self.cname:
            return f"https://{self.cname}/{encoded_key}"
            
        # Get endpoint without protocol
        endpoint = self.bucket.endpoint.replace('http://', '').replace('https://', '')
        if self.internal:
            # Convert normal endpoint to internal endpoint
            if 'oss-internal' not in endpoint:
                endpoint = endpoint.replace('oss.', 'oss-internal.')
        return f"https://{self.bucket_name}.{endpoint}/{encoded_key}" 