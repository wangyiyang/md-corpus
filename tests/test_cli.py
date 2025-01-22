import pytest
import os
from click.testing import CliRunner
from md_corpus.cli import cli
from md_corpus import __version__

@pytest.fixture
def runner():
    return CliRunner()

def test_version_command(runner):
    result = runner.invoke(cli, ['version'])
    assert result.exit_code == 0
    assert f"md-corpus version {__version__}" in result.output

def test_version_option(runner):
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert f"md-corpus, version {__version__}" in result.output

def test_convert_missing_required_options(runner):
    result = runner.invoke(cli, ['convert', 'tests/data'])
    assert result.exit_code == 2
    assert "Missing option '--provider'" in result.output

def test_convert_invalid_provider(runner):
    result = runner.invoke(cli, ['convert', 'tests/data', '--provider', 'invalid'])
    assert result.exit_code == 2
    assert "Invalid value for '--provider'" in result.output

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip integration tests in CI environment")
def test_convert_success(runner, tmp_path):
    """Test successful conversion with test credentials"""
    # Create test files
    test_file = tmp_path / "test.md"
    test_file.write_text("![test](./image/test.jpg)")
    
    image_dir = tmp_path / "image"
    image_dir.mkdir()
    (image_dir / "test.jpg").write_bytes(b"test image")

    result = runner.invoke(cli, [
        'convert',
        str(test_file),
        '--provider', 'aliyun',
        '--bucket', 'test-bucket',
        '--access-key', 'test-key',
        '--secret-key', 'test-secret',
        '--endpoint', 'https://oss-cn-beijing.aliyuncs.com'
    ])
    assert result.exit_code == 0
    assert "Processing file:" in result.output
    assert "Done!" in result.output

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip integration tests in CI environment")
def test_convert_with_env_credentials(runner, tmp_path, monkeypatch):
    """Test conversion using environment variables for credentials"""
    # Create test files
    test_file = tmp_path / "test.md"
    test_file.write_text("![test](./image/test.jpg)")
    
    image_dir = tmp_path / "image"
    image_dir.mkdir()
    (image_dir / "test.jpg").write_bytes(b"test image")

    # Set environment variables
    monkeypatch.setenv('ALI_OSS_ACCESS_KEY_ID', 'test-key')
    monkeypatch.setenv('ALI_OSS_ACCESS_KEY_SECRET', 'test-secret')
    monkeypatch.setenv('ALI_OSS_BUCKET', 'test-bucket')
    monkeypatch.setenv('ALI_OSS_ENDPOINT', 'https://oss-cn-beijing.aliyuncs.com')
    
    result = runner.invoke(cli, [
        'convert',
        str(test_file),
        '--provider', 'aliyun',
        '--bucket', 'test-bucket'  # Still need to provide bucket name
    ])
    assert result.exit_code == 0 