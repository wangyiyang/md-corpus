"""AWS S3 storage provider implementation"""

import os
from pathlib import Path
import mimetypes
import boto3
from botocore.exceptions import ClientError

from .base import StorageProvider
from ..exceptions import MDCorpusError

class AWSProvider(StorageProvider):
    """AWS S3 storage provider"""
    
    def __init__(
        self,
        bucket: str,
        access_key: str = None,
        secret_key: str = None,
        region: str = None,
        endpoint_url: str = None,
        cname: str = None
    ):
        """Initialize AWS S3 provider
        
        Args:
            bucket: S3 bucket name
            access_key: AWS access key ID (optional, can be set via AWS_ACCESS_KEY_ID env var)
            secret_key: AWS secret access key (optional, can be set via AWS_SECRET_ACCESS_KEY env var)
            region: AWS region (optional, can be set via AWS_DEFAULT_REGION env var)
            endpoint_url: Custom endpoint URL for S3 compatible services
            cname: Custom domain name (CNAME) for the bucket
        """
        self.bucket_name = bucket
        self.region = region or os.getenv('AWS_DEFAULT_REGION')
        self.cname = cname
        
        if not self.region:
            raise MDCorpusError("AWS region is required")
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=self.region,
            endpoint_url=endpoint_url
        )
    
    def upload_file(self, file_path: str) -> str:
        """Upload a file to S3
        
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
        
        # Generate S3 key from file path
        key = str(file_path.name)
        
        # Detect content type
        content_type = mimetypes.guess_type(file_path)[0]
        extra_args = {
            'ContentType': content_type,
            'ACL': 'public-read'  # Set file to be publicly readable
        } if content_type else {'ACL': 'public-read'}
        
        try:
            self.s3.upload_file(
                str(file_path),
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            return self.get_file_url(key)
        except ClientError as e:
            raise MDCorpusError(f"Failed to upload file to S3: {str(e)}")
    
    def get_file_url(self, file_key: str) -> str:
        """Get the public URL for a file in S3
        
        Args:
            file_key: Key of the file in S3
            
        Returns:
            str: Public URL of the file
        """
        if self.cname:
            return f"https://{self.cname}/{file_key}"
        return f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}" 