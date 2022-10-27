#!/usr/bin/env python
from core.builder import Builder
import click

open_help = "If specified, then the live server will automatically open in the browser."
tailwind_help = "Enable tailwind compiling"
template_help = "Specify the type of template you would like to start with. Default 'blank'"


@click.group()
def cli():
    '''Group of all commands for this package.'''


@cli.command(name="new")
@click.option("--sass", flag_value=True, help=open_help, default=False)
@click.option("--tailwind", flag_value=True, help=tailwind_help, default=False)
@click.option("--no_defaults", flag_value=True, help=tailwind_help, default=False)
@click.option("--template", type=str, show_default=True, help=template_help, default="blank")
def new_command(sass: bool, tailwind: bool, no_defaults: bool, template: str):
    from core.new import generate

    print(template)
    generate(sass=sass, tailwind=tailwind, no_defaults=no_defaults, template=template)


@cli.command(name="serve")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
def serve_command(open: bool, debug: bool):
    raise NotImplementedError("The live serve has not been implemented yet")


# @click.option("-o", "--open", flag_value=True, help=open_help, default=False)s
# @click.option("-d", "--debug", flag_value=True, help=debug_help, default=False)
@cli.command(name="build")
def build_command():
    from core.builder import Builder

    Builder().full()


if __name__ == "__main__":
    cli()
