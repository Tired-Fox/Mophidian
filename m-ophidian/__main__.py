#!/usr/bin/env python
from mimetypes import init
import click

open_help = "If specified, then the live server will automatically open in the browser."

@click.group()
def cli():
    '''Group of all commands for this package.'''

@cli.command(name="serve")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
def serve_command(open: bool):
    from commands import liveserver
    liveserver(open)
    
@cli.command(name="build")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
def serve_command(open: bool):
    from compiler.setup import init_static
    init_static()
    
if __name__ == "__main__":
    cli()
