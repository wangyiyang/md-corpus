"""Storage providers for md-corpus"""

from .base import StorageProvider
from .aws import AWSProvider
from .aliyun import AliyunProvider

__all__ = ['StorageProvider', 'AWSProvider', 'AliyunProvider'] 