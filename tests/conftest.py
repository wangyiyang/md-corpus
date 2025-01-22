import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Try to load .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory"""
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def aliyun_credentials():
    """Return Aliyun OSS credentials from environment variables"""
    return {
        "access_key": os.getenv("ALI_OSS_ACCESS_KEY_ID", "test-key"),
        "secret_key": os.getenv("ALI_OSS_ACCESS_KEY_SECRET", "test-secret"),
        "bucket": os.getenv("ALI_OSS_BUCKET", "test-bucket"),
        "endpoint": os.getenv("ALI_OSS_ENDPOINT", "https://oss-cn-beijing.aliyuncs.com")
    }

@pytest.fixture(scope="session")
def aws_credentials():
    """Return AWS S3 credentials from environment variables"""
    return {
        "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
        "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "bucket": os.getenv("AWS_BUCKET"),
        "region": os.getenv("AWS_REGION", "us-east-1")
    } 