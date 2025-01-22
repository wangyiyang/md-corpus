import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv(Path(__file__).parent / ".env")

@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to the test data directory"""
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def aliyun_credentials():
    """Return Aliyun OSS credentials from environment variables"""
    return {
        "access_key": os.getenv("ALI_OSS_ACCESS_KEY_ID"),
        "secret_key": os.getenv("ALI_OSS_ACCESS_KEY_SECRET"),
        "bucket": os.getenv("ALI_OSS_BUCKET"),
        "endpoint": os.getenv("ALI_OSS_ENDPOINT")
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