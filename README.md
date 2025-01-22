# md-corpus

A Python package for integrating Markdown files with cloud object storage services.

## Features

- Automatically convert local resource links in Markdown files to object storage URLs
- Support for multiple Markdown files in a directory
- Support for AWS S3 and Aliyun OSS
- Both CLI tool and programmable API
- Extensible adapter/plugin mechanism
- Support for custom domains (CNAME) for both AWS S3 and Aliyun OSS
- Support for internal endpoints (Aliyun OSS)

## Installation

```bash
pip install md-corpus
```

## Usage

### Command Line Interface

Convert a single Markdown file:
```bash
# Using AWS S3
md-corpus convert file.md --provider aws --bucket my-bucket --region us-east-1 --cname cdn.example.com

# Using Aliyun OSS
md-corpus convert file.md --provider aliyun --bucket my-bucket --endpoint oss-cn-beijing.aliyuncs.com --cname cdn.example.com
```

Convert all Markdown files in a directory:
```bash
# Using AWS S3
md-corpus convert ./docs --provider aws --bucket my-bucket --region us-east-1 --cname cdn.example.com

# Using Aliyun OSS with internal endpoint
md-corpus convert ./docs --provider aliyun --bucket my-bucket --endpoint oss-cn-beijing.aliyuncs.com --internal --cname cdn.example.com
```

All command line options:
```bash
md-corpus convert [PATH] --provider [aws|aliyun] --bucket BUCKET [OPTIONS]

Options:
  --provider [aws|aliyun]  Storage provider to use (required)
  --bucket TEXT           Storage bucket name (required)
  --access-key TEXT       Provider access key (can use env vars)
  --secret-key TEXT       Provider secret key (can use env vars)
  --region TEXT          AWS region (for AWS provider)
  --endpoint TEXT        Storage endpoint (for Aliyun provider)
  --internal            Use internal endpoint (for Aliyun provider)
  --cname TEXT          Custom domain name (CNAME) for the bucket
```

### Python API

#### AWS S3 Example

```python
from md_corpus import MDCorpus
from md_corpus.providers import AWSProvider

# Initialize the provider
provider = AWSProvider(
    bucket="my-bucket",
    access_key="your-access-key",  # Optional, can use AWS_ACCESS_KEY_ID env var
    secret_key="your-secret-key",  # Optional, can use AWS_SECRET_ACCESS_KEY env var
    region="us-east-1",           # Optional, can use AWS_DEFAULT_REGION env var
    cname="cdn.example.com"       # Optional, custom domain name
)

# Create MDCorpus instance
corpus = MDCorpus(provider)

# Convert a single file
corpus.convert_file("path/to/file.md")

# Convert a directory
corpus.convert_directory("path/to/docs")
```

#### Aliyun OSS Example

```python
from md_corpus import MDCorpus
from md_corpus.providers import AliyunProvider

# Initialize the provider
provider = AliyunProvider(
    bucket="my-bucket",
    access_key="your-access-key",  # Optional, can use ALI_OSS_ACCESS_KEY_ID env var
    secret_key="your-secret-key",  # Optional, can use ALI_OSS_ACCESS_KEY_SECRET env var
    endpoint="oss-cn-beijing.aliyuncs.com",  # Optional, can use ALI_OSS_ENDPOINT env var
    internal=False,                # Optional, use internal endpoint
    cname="cdn.example.com"        # Optional, custom domain name
)

# Create MDCorpus instance
corpus = MDCorpus(provider)

# Convert files
corpus.convert_file("path/to/file.md")
corpus.convert_directory("path/to/docs")
```

## Configuration

The package can be configured using environment variables:

### AWS S3 Environment Variables
- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key
- `AWS_DEFAULT_REGION`: AWS region

### Aliyun OSS Environment Variables
- `ALI_OSS_ACCESS_KEY_ID`: Aliyun access key ID
- `ALI_OSS_ACCESS_KEY_SECRET`: Aliyun access key secret
- `ALI_OSS_ENDPOINT`: OSS endpoint

## Features

### Custom Domain (CNAME)
Both AWS S3 and Aliyun OSS support using custom domains for your bucket. This can be configured using the `cname` parameter:

```python
provider = AWSProvider(bucket="my-bucket", cname="cdn.example.com")
# or
provider = AliyunProvider(bucket="my-bucket", cname="cdn.example.com")
```

### Internal Endpoints (Aliyun OSS)
When running in Aliyun ECS, you can use internal endpoints to reduce data transfer costs:

```python
provider = AliyunProvider(
    bucket="my-bucket",
    endpoint="oss-cn-beijing.aliyuncs.com",
    internal=True  # Will use oss-internal.aliyuncs.com
)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.