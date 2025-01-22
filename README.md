# md-corpus

A Python package for integrating Markdown files with cloud object storage. It helps you:
- Format Markdown files using consistent style
- Upload images to cloud storage (Aliyun OSS, AWS S3)
- Convert local image links to cloud storage URLs

## Requirements

- Python >= 3.10
- Dependencies:
  - boto3 (AWS S3 support)
  - oss2 (Aliyun OSS support)
  - click (CLI tool)
  - markdown (Markdown processing)
  - mdformat (Markdown formatting)

## Installation

```bash
# Install from PyPI
pip install md-corpus

# Or install from source
git clone https://github.com/wangyiyang/md-corpus.git
cd md-corpus
pip install -e .
```

## Features

### 1. Format Markdown Files

Format your Markdown files using consistent style:
```bash
# Format a single file
md-corpus format path/to/file.md

# Format all Markdown files in a directory (including subdirectories)
md-corpus format path/to/directory
```

The formatter will:
- Use `-` for list items (mdformat default)
- Ensure consistent heading styles
- Maintain code blocks and their language specifications
- Preserve blank lines for readability

### 2. Convert Image Links

Convert local image links to cloud storage URLs:
```bash
# Convert a single file
md-corpus convert path/to/file.md --provider aliyun --bucket your-bucket

# Convert all Markdown files in a directory
md-corpus convert path/to/directory --provider aliyun --bucket your-bucket
```

When converting files, md-corpus will:
1. Format the Markdown content for consistent style
2. Upload referenced images to cloud storage
3. Update image links to use cloud storage URLs

## Cloud Storage Providers

### Aliyun OSS

```bash
# Using command line arguments
md-corpus convert file.md \
    --provider aliyun \
    --bucket your-bucket \
    --access-key your-access-key \
    --secret-key your-secret-key \
    --endpoint https://oss-cn-beijing.aliyuncs.com

# Using environment variables
export ALI_OSS_ACCESS_KEY_ID=your-access-key
export ALI_OSS_ACCESS_KEY_SECRET=your-secret-key
export ALI_OSS_BUCKET=your-bucket
export ALI_OSS_ENDPOINT=https://oss-cn-beijing.aliyuncs.com

md-corpus convert file.md --provider aliyun
```

### AWS S3

```bash
# Using command line arguments
md-corpus convert file.md \
    --provider aws \
    --bucket your-bucket \
    --access-key your-access-key \
    --secret-key your-secret-key \
    --region us-east-1

# Using environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_BUCKET=your-bucket
export AWS_REGION=us-east-1

md-corpus convert file.md --provider aws
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/wangyiyang/md-corpus.git
cd md-corpus
```

2. Create a conda environment:
```bash
conda create -n md-corpus python=3.10
conda activate md-corpus
```

3. Install development dependencies:
```bash
pip install -e .
```

4. Run tests:
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License