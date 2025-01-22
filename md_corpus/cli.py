"""Command line interface for md-corpus"""

import os
import click
from pathlib import Path
from . import MDCorpus, __version__
from .providers import AliyunProvider, AWSProvider
from .exceptions import MDCorpusError

@click.group()
@click.version_option(version=__version__, prog_name="md-corpus")
def cli():
    """md-corpus - A tool for integrating Markdown files with cloud storage"""
    pass

@cli.command()
def version():
    """Show version information"""
    click.echo(f"md-corpus version {__version__}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--provider', type=click.Choice(['aliyun', 'aws']), required=True,
              help='Cloud storage provider to use')
@click.option('--bucket', help='Storage bucket name')
@click.option('--access-key', help='Provider access key')
@click.option('--secret-key', help='Provider secret key')
@click.option('--endpoint', help='Aliyun OSS endpoint')
@click.option('--region', help='AWS region')
def convert(path, provider, bucket, access_key, secret_key, endpoint=None, region=None):
    """Convert local resource links to cloud storage URLs"""
    try:
        # Get credentials from environment if not provided
        bucket = bucket or os.getenv(f"{provider.upper()}_BUCKET")
        access_key = access_key or os.getenv(f"{provider.upper()}_ACCESS_KEY_ID")
        secret_key = secret_key or os.getenv(f"{provider.upper()}_ACCESS_KEY_SECRET")
        
        if provider == 'aliyun':
            endpoint = endpoint or os.getenv("ALI_OSS_ENDPOINT")
            storage = AliyunProvider(bucket, access_key, secret_key, endpoint)
        else:
            region = region or os.getenv("AWS_REGION", "us-east-1")
            storage = AWSProvider(bucket, access_key, secret_key, region)
            
        corpus = MDCorpus(storage)
        path = Path(path)
        
        if path.is_file():
            click.echo(f"Processing file: {path}")
            corpus.convert_file(path)
        else:
            click.echo(f"Processing directory: {path}")
            processed = corpus.convert_directory(path)
            click.echo(f"Processed {len(processed)} files")
            
        click.echo("Done!")
        
    except MDCorpusError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def format(path):
    """Format Markdown files"""
    try:
        # We don't need a real provider for formatting
        corpus = MDCorpus(None)
        path = Path(path)
        
        if path.is_file():
            click.echo(f"Formatting file: {path}")
            corpus.format_file(path)
        else:
            click.echo(f"Formatting directory: {path}")
            processed = corpus.format_directory(path)
            click.echo(f"Formatted {len(processed)} files")
            
        click.echo("Done!")
        
    except MDCorpusError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

def main():
    cli() 