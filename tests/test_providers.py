import pytest
import os
from md_corpus.providers import AWSProvider, AliyunProvider
from md_corpus.exceptions import MDCorpusError

from tests.test_core import MockStorageProvider

def test_aliyun_provider_init():
    provider = AliyunProvider(
        bucket="test-bucket",
        access_key="test-key",
        secret_key="test-secret",
        endpoint="https://oss-cn-beijing.aliyuncs.com"
    )
    assert provider.bucket_name == "test-bucket"
    assert provider.internal is False

def test_aliyun_provider_init_internal():
    provider = AliyunProvider(
        bucket="test-bucket",
        access_key="test-key",
        secret_key="test-secret",
        endpoint="https://oss-cn-beijing.aliyuncs.com",
        internal=True
    )
    assert provider.internal is True

def test_aws_provider_init():
    provider = AWSProvider(
        bucket="test-bucket",
        access_key="test-key",
        secret_key="test-secret",
        region="us-east-1"
    )
    assert provider.bucket_name == "test-bucket"
    assert provider.region == "us-east-1"

def test_aws_provider_missing_region():
    with pytest.raises(MDCorpusError):
        AWSProvider(
            bucket="test-bucket",
            access_key="test-key",
            secret_key="test-secret"
        )

def test_aliyun_provider_missing_endpoint(monkeypatch):
    """Test that AliyunProvider raises error when endpoint is missing"""
    # Clear environment variables
    monkeypatch.delenv('ALI_OSS_ENDPOINT', raising=False)
    
    with pytest.raises(MDCorpusError, match="Missing required Aliyun OSS endpoint"):
        AliyunProvider(
            bucket="test-bucket",
            access_key="test-key",
            secret_key="test-secret"
        )

@pytest.mark.integration
def test_aliyun_provider_integration(aliyun_credentials, tmp_path):
    """Integration test with real Aliyun OSS credentials"""
    # Skip if using test credentials
    if aliyun_credentials["access_key"] == "test-key":
        pytest.skip("Test credentials not suitable for integration test")
        
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_content = b"Hello, Aliyun OSS!"
    test_file.write_bytes(test_content)
    
    # Initialize provider with real credentials
    provider = AliyunProvider(
        bucket=aliyun_credentials["bucket"],
        access_key=aliyun_credentials["access_key"],
        secret_key=aliyun_credentials["secret_key"],
        endpoint=aliyun_credentials["endpoint"]
    )
    
    # Upload file and get URL
    url = provider.upload_file(test_file)
    
    # Verify URL format
    assert url.startswith(f"https://{aliyun_credentials['bucket']}.oss-cn-beijing.aliyuncs.com/")
    assert url.endswith("test.txt")

@pytest.mark.integration
def test_aliyun_provider_integration_with_internal(aliyun_credentials, tmp_path):
    """Integration test with internal endpoint"""
    # Skip if using test credentials
    if aliyun_credentials["access_key"] == "test-key":
        pytest.skip("Test credentials not suitable for integration test")
        
    test_file = tmp_path / "test-internal.txt"
    test_content = b"Hello, Internal Aliyun OSS!"
    test_file.write_bytes(test_content)
    
    provider = AliyunProvider(
        bucket=aliyun_credentials["bucket"],
        access_key=aliyun_credentials["access_key"],
        secret_key=aliyun_credentials["secret_key"],
        endpoint=aliyun_credentials["endpoint"],
        internal=True
    )
    
    # Upload should succeed even with internal endpoint
    url = provider.upload_file(test_file)
    
    # The returned URL should still be public
    assert url.startswith(f"https://{aliyun_credentials['bucket']}.oss-cn-beijing.aliyuncs.com/")

def test_provider_upload_error(tmp_path):
    """Test error handling during file upload"""
    class ErrorProvider(MockStorageProvider):
        def upload_file(self, file_path):
            raise MDCorpusError("Upload failed")
    
    provider = ErrorProvider()
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")
    
    with pytest.raises(MDCorpusError) as exc:
        provider.upload_file(test_file)
    assert "Upload failed" in str(exc.value)

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("AWS_ACCESS_KEY_ID"), reason="AWS credentials not available")
def test_aws_provider_integration(aws_credentials, tmp_path):
    """Integration test with AWS S3"""
    test_file = tmp_path / "test.txt"
    test_content = b"Hello, AWS S3!"
    test_file.write_bytes(test_content)
    
    provider = AWSProvider(
        bucket=aws_credentials["bucket"],
        access_key=aws_credentials["access_key"],
        secret_key=aws_credentials["secret_key"],
        region=aws_credentials["region"]
    )
    
    url = provider.upload_file(test_file)
    assert url.startswith(f"https://{aws_credentials['bucket']}.s3.{aws_credentials['region']}.amazonaws.com/") 