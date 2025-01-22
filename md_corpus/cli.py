"""Command line interface for md-corpus"""

import click
from pathlib import Path

from . import MDCorpus, __version__
from .providers import AWSProvider, AliyunProvider
from .exceptions import MDCorpusError

@click.group()
@click.version_option(version=__version__, prog_name='md-corpus')
def cli():
    """md-corpus - Convert local resource links in Markdown files to cloud storage URLs"""
    pass

@cli.command()
def version():
    """Show the version of md-corpus"""
    click.echo(f"md-corpus version {__version__}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--provider', type=click.Choice(['aws', 'aliyun']), required=True,
              help='Storage provider to use')
@click.option('--bucket', required=True, help='Storage bucket name')
@click.option('--access-key', help='Provider access key')
@click.option('--secret-key', help='Provider secret key')
@click.option('--region', help='AWS region (for AWS provider)')
@click.option('--endpoint', help='Storage endpoint (for Aliyun provider)')
@click.option('--internal', is_flag=True, help='Use internal endpoint (for Aliyun provider)')
@click.option('--cname', help='Custom domain name (CNAME) for the bucket')
def convert(path, provider, bucket, access_key, secret_key, region, endpoint, internal, cname):
    """Convert local resource links in Markdown files to cloud storage URLs
    
    PATH can be a single Markdown file or a directory containing Markdown files
    """
    try:
        # Initialize provider
        if provider == 'aws':
            storage = AWSProvider(
                bucket=bucket,
                access_key=access_key,
                secret_key=secret_key,
                region=region,
                cname=cname
            )
        else:  # aliyun
            storage = AliyunProvider(
                bucket=bucket,
                access_key=access_key,
                secret_key=secret_key,
                endpoint=endpoint,
                internal=internal,
                cname=cname
            )
        
        # Initialize MDCorpus
        corpus = MDCorpus(storage)
        
        # Process file or directory
        path = Path(path)
        if path.is_file():
            click.echo(f"Processing file: {path}")
            corpus.convert_file(path)
            click.echo("Done!")
        else:
            click.echo(f"Processing directory: {path}")
            processed = corpus.convert_directory(path)
            click.echo(f"Processed {len(processed)} files:")
            for file in processed:
                click.echo(f"  - {file}")
            
    except MDCorpusError as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)

def main():
    """Entry point for the command line interface"""
    cli() 