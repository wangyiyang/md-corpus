import pytest
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

def test_convert_success(runner, test_data_dir, aliyun_credentials):
    """Test successful conversion with Aliyun credentials"""
    result = runner.invoke(cli, [
        'convert',
        str(test_data_dir / 'test1.md'),
        '--provider', 'aliyun',
        '--bucket', aliyun_credentials['bucket'],
        '--access-key', aliyun_credentials['access_key'],
        '--secret-key', aliyun_credentials['secret_key'],
        '--endpoint', aliyun_credentials['endpoint']
    ])
    assert result.exit_code == 0
    assert "Processing file:" in result.output
    assert "Done!" in result.output

def test_convert_with_env_credentials(runner, test_data_dir, monkeypatch):
    """Test conversion using environment variables for credentials"""
    # Set environment variables
    monkeypatch.setenv('ALI_OSS_ACCESS_KEY_ID', 'test-key')
    monkeypatch.setenv('ALI_OSS_ACCESS_KEY_SECRET', 'test-secret')
    monkeypatch.setenv('ALI_OSS_BUCKET', 'test-bucket')
    monkeypatch.setenv('ALI_OSS_ENDPOINT', 'https://oss-cn-beijing.aliyuncs.com')
    
    result = runner.invoke(cli, [
        'convert',
        str(test_data_dir / 'test1.md'),
        '--provider', 'aliyun',
        '--bucket', 'test-bucket'  # Still need to provide bucket name
    ])
    assert result.exit_code == 0 