#!/usr/bin/env python
import click

open_help = "If specified, then the live server will automatically open in the browser."


@click.group()
def cli():
    '''Group of all commands for this package.'''


@cli.command(name="serve")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
def serve_command(open: bool):
    from liveserver.serve import serve as liveserver

    liveserver(open)


@cli.command(name="build")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
def build_command(open: bool):
    from compiler.build import Build

    build = Build()
    build.full()


if __name__ == "__main__":
    cli()
