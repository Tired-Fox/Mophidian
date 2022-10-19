#!/usr/bin/env python
import click

open_help = "If specified, then the live server will automatically open in the browser."
tailwind_help = "Enable tailwind compiling"


@click.group()
def cli():
    '''Group of all commands for this package.'''


@cli.command(name="new")
@click.option("--sass", flag_value=True, help=open_help, default=False)
@click.option("--tailwind", flag_value=True, help=tailwind_help, default=False)
@click.option("--no_defaults", flag_value=True, help=tailwind_help, default=False)
def new_command(sass: bool, tailwind: bool, no_defaults: bool):
    from new import generate

    generate(sass=sass, tailwind=tailwind, no_defaults=no_defaults)


@cli.command(name="serve")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
@click.option("-t", "--tailwind", flag_value=True, help=tailwind_help, default=False)
def serve_command(open: bool, tailwind: bool):
    from liveserver.serve import serve as liveserver

    liveserver(open)


@cli.command(name="build")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
@click.option("-t", "--tailwind", flag_value=True, help=tailwind_help, default=False)
def build_command(open: bool, tailwind: bool):
    from compiler.build import Build

    build = Build(tailwind)
    build.full()
    if open:
        pass


if __name__ == "__main__":
    cli()
