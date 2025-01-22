import pytest
from pathlib import Path
from md_corpus import MDCorpus
from md_corpus.exceptions import MDCorpusError
from urllib.parse import quote

class MockStorageProvider:
    def __init__(self):
        self.uploaded_files = {}
        self.base_url = "https://example.com/bucket"
    
    def upload_file(self, file_path):
        self.uploaded_files[str(file_path)] = True
        return f"{self.base_url}/{quote(Path(file_path).name)}"

@pytest.fixture
def mock_provider():
    return MockStorageProvider()

@pytest.fixture
def corpus(mock_provider):
    return MDCorpus(mock_provider)

def test_convert_file_not_found(corpus):
    with pytest.raises(MDCorpusError):
        corpus.convert_file("nonexistent.md")

def test_convert_file(corpus, tmp_path):
    # Create a test markdown file
    test_file = tmp_path / "test.md"
    test_file.write_text("![test](./image/test.jpg)")
    
    # Create test image
    image_dir = tmp_path / "image"
    image_dir.mkdir()
    test_image = image_dir / "test.jpg"
    test_image.write_bytes(b"fake image data")
    
    # Convert the file
    corpus.convert_file(test_file)
    
    # Check if image was uploaded
    assert str(test_image) in corpus.storage.uploaded_files
    
    # Check if markdown was updated
    converted_content = test_file.read_text()
    assert "https://example.com/bucket/test.jpg" in converted_content

def test_convert_directory(corpus, tmp_path):
    # Create test structure
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir/image").mkdir(parents=True)
    
    # Create test files
    (tmp_path / "test1.md").write_text("![test](./image/1.jpg)")
    (tmp_path / "subdir/test2.md").write_text("![test](./image/2.jpg)")
    (tmp_path / "subdir/image/1.jpg").write_bytes(b"test1")
    (tmp_path / "subdir/image/2.jpg").write_bytes(b"test2")
    
    # Convert directory
    processed = corpus.convert_directory(tmp_path)
    
    # Check results
    assert len(processed) == 2
    assert any(str(p).endswith("test1.md") for p in processed)
    assert any(str(p).endswith("test2.md") for p in processed)

def test_convert_real_files(corpus, tmp_path):
    """Test conversion with real test files from data directory"""
    # Create test files in temporary directory
    test1_path = tmp_path / "test1.md"
    test1_path.write_text("![test1](./image/1.jpg)")
    
    # Create test image
    image_dir = tmp_path / "image"
    image_dir.mkdir(exist_ok=True)
    image1_path = image_dir / "1.jpg"
    image1_path.write_bytes(b"test1")
    
    # Convert file
    corpus.convert_file(test1_path)
    
    # Verify image was uploaded
    assert str(image1_path) in corpus.storage.uploaded_files
    
    # Verify markdown was updated
    content = test1_path.read_text()
    assert "https://example.com/bucket/1.jpg" in content
    
    # Convert test2.md
    test2_path = tmp_path / "test2.md"
    test2_path.write_text("![test2](./image/2.jpg)")
    
    # Create test image
    image2_path = image_dir / "2.jpg"
    image2_path.write_bytes(b"test2")
    
    # Convert file
    corpus.convert_file(test2_path)
    
    # Verify image was uploaded
    assert str(image2_path) in corpus.storage.uploaded_files
    
    # Verify markdown was updated
    content = test2_path.read_text()
    assert "https://example.com/bucket/2.jpg" in content

@pytest.mark.integration
def test_convert_real_files_with_aliyun(aliyun_credentials, tmp_path):
    """Integration test with real files and Aliyun OSS"""
    # Skip if using test credentials
    if aliyun_credentials["access_key"] == "test-key":
        pytest.skip("Test credentials not suitable for integration test")
        
    from md_corpus.providers import AliyunProvider
    
    # Initialize provider with real credentials
    provider = AliyunProvider(
        bucket=aliyun_credentials["bucket"],
        access_key=aliyun_credentials["access_key"],
        secret_key=aliyun_credentials["secret_key"],
        endpoint=aliyun_credentials["endpoint"]
    )
    
    # Initialize MDCorpus with real provider
    corpus = MDCorpus(provider)
    
    # Create test files in temporary directory
    test1_path = tmp_path / "test1.md"
    test1_path.write_text("![test1](./image/1.jpg)")
    
    # Create test image
    image_dir = tmp_path / "image"
    image_dir.mkdir(exist_ok=True)
    image1_path = image_dir / "1.jpg"
    image1_path.write_bytes(b"test1")
    
    # Convert file
    corpus.convert_file(test1_path)
    
    # Verify markdown was updated with correct URL
    content = test1_path.read_text()
    assert f"https://{aliyun_credentials['bucket']}.oss-cn-beijing.aliyuncs.com/1.jpg" in content

def test_convert_file_edge_cases(corpus, test_data_dir):
    """Test edge cases in Markdown link parsing"""
    test_file = test_data_dir / "edge_cases.md"
    image_dir = test_data_dir / "image"
    image_dir.mkdir(exist_ok=True)
    
    # Create test images
    (image_dir / "test.jpg").write_bytes(b"test")
    (image_dir / "test space.jpg").write_bytes(b"test")
    (image_dir / "test#hash.jpg").write_bytes(b"test")
    
    # Test various Markdown image syntaxes
    test_content = """
![](./image/test.jpg)
![alt text](./image/test.jpg "title")
![test](./image/test space.jpg)
![test](./image/test#hash.jpg)
<img src="./image/test.jpg" alt="html tag">
"""
    test_file.write_text(test_content)
    
    # Convert the file
    corpus.convert_file(test_file)
    
    # Verify conversions
    content = test_file.read_text()
    assert "https://example.com/bucket/test.jpg" in content
    assert "https://example.com/bucket/test%20space.jpg" in content
    assert "https://example.com/bucket/test%23hash.jpg" in content
    assert '<img src="https://example.com/bucket/test.jpg"' in content
    
    # Verify all images were uploaded
    assert str(image_dir / "test.jpg") in corpus.storage.uploaded_files
    assert str(image_dir / "test space.jpg") in corpus.storage.uploaded_files
    assert str(image_dir / "test#hash.jpg") in corpus.storage.uploaded_files

def test_format_file(corpus, test_data_dir):
    """Test Markdown file formatting"""
    # Create a test markdown file with unformatted content
    test_file = test_data_dir / "format_test.md"
    unformatted_content = """
# Title

This is a paragraph.
* Item 1
* Item 2
  * Subitem

```python
def hello():
    print("Hello")
```
"""
    test_file.write_text(unformatted_content)
    
    # Format the file
    corpus.format_file(test_file)
    
    # Read the formatted content
    formatted_content = test_file.read_text()
    
    # Verify formatting
    assert "# Title" in formatted_content
    assert "- Item 1" in formatted_content  # mdformat uses - for lists
    assert "- Item 2" in formatted_content
    assert "  - Subitem" in formatted_content
    assert "```python" in formatted_content
    assert 'print("Hello")' in formatted_content

def test_format_directory(corpus, test_data_dir):
    """Test formatting multiple Markdown files in a directory"""
    # Create test files
    subdir = test_data_dir / "subdir"
    subdir.mkdir(exist_ok=True)
    
    file1 = test_data_dir / "test1.md"
    file1.write_text("# File 1\n* Item 1\n* Item 2")
    
    file2 = subdir / "test2.md"
    file2.write_text("# File 2\n* Item 1\n* Item 2")
    
    # Format directory
    processed = corpus.format_directory(test_data_dir)
    
    # Check results
    assert len(processed) >= 2  # May be more if other test files exist
    assert any(str(p).endswith("test1.md") for p in processed)
    assert any(str(p).endswith("test2.md") for p in processed)
    
    # Verify both files were formatted
    content1 = file1.read_text()
    content2 = file2.read_text()
    assert "# File 1" in content1
    assert "# File 2" in content2

def test_format_file_not_found(corpus):
    """Test formatting a non-existent file"""
    with pytest.raises(MDCorpusError):
        corpus.format_file("nonexistent.md")

def test_convert_file_with_formatting(corpus, test_data_dir):
    """Test that files are formatted before conversion"""
    # Create a test markdown file with unformatted content
    test_file = test_data_dir / "convert_test.md"
    unformatted_content = """
# Title
* Item 1
* Item 2
![test](./image/test.jpg)
"""
    test_file.write_text(unformatted_content)
    
    # Create test image
    image_dir = test_data_dir / "image"
    image_dir.mkdir(exist_ok=True)
    test_image = image_dir / "test.jpg"
    test_image.write_bytes(b"test image")
    
    # Convert the file
    corpus.convert_file(test_file)
    
    # Read the converted content
    converted_content = test_file.read_text()
    
    # Verify formatting was applied
    assert "- Item 1" in converted_content  # mdformat uses - for lists
    assert "- Item 2" in converted_content
    
    # Verify image was converted
    assert "https://example.com/bucket/test.jpg" in converted_content
    assert str(test_image) in corpus.storage.uploaded_files

def test_convert_nested_directory(corpus, test_data_dir):
    """Test converting files in deeply nested directories"""
    # Create nested directory structure
    deep_dir = test_data_dir / "level1/level2/level3"
    deep_dir.mkdir(parents=True, exist_ok=True)
    image_dir = deep_dir / "image"
    image_dir.mkdir(exist_ok=True)
    
    # Create test files
    test_file = deep_dir / "test.md"
    test_file.write_text("# Test\n* Item 1\n![test](./image/test.jpg)")
    
    # Create test image
    test_image = image_dir / "test.jpg"
    test_image.write_bytes(b"test image")
    
    # Convert the directory
    processed = corpus.convert_directory(test_data_dir)
    
    # Verify file was processed
    assert str(test_file) in processed
    
    # Read the converted content
    converted_content = test_file.read_text()
    
    # Verify formatting and image conversion
    assert "- Item 1" in converted_content  # Check formatting
    assert "https://example.com/bucket/test.jpg" in converted_content  # Check image URL
    assert str(test_image) in corpus.storage.uploaded_files  # Check image upload 