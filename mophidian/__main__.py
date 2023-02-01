#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import click
from shutil import rmtree

from teddecor import TED, Logger, LogLevel

from mophidian.core import build as full_build
from mophidian.config import CONFIG, build_config
from mophidian import states, DestState
from .Server.server import Server, LiveServer


@click.group()
def cli():
    '''Pythonic Static Site Generator CLI.'''

@click.option("-d", "--debug", flag_value=True, help="Enable debug logs", default=False)
@click.option("-f", "--files", flag_value=True, help="Log the files that were found in the build process", default=False)
@cli.command(name="build", help=f"Compile and build the website to {CONFIG.site.dest!r}")
def build_command(debug: bool, files: bool):
    """Build the website in the specified dest directory."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    states["dest"] = DestState.PREVIEW
    full_build(files)

@click.argument("style", default="")
@click.option("-l", "--list", flag_value=True, help="list the possible color themes. Allows for style selection.", default=False)
@cli.command(name="highlight", help="Generate a pygmentize CSS file")
def code_highlight(style: str, list: bool):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """
    from mophidian.cli.styles import generate_highlight

    generate_highlight(style, list)

@click.argument("name", default="")
@click.option("-f", "--force", flag_value=True, help="force write files and directories even if they already exist", default=False)
@click.option("-p", "--preset", flag_value=True, help="generate the project with a preset", default=False)
@cli.command(name="new", help="Create a new mophidian project")
def new(force: bool, preset: bool, name: str):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """

    while name == "":
        name = input("Enter the name of your project: ")

    Logger.Info("Generating file strucutre")

    path = Path(name.lower())

    if path.is_dir():
        if force:
            rmtree(path)
        else:
            Logger.error(
                TED.parse(
                    f"Failed to create project [@Fyellow]/{name}[@F] since it already exists"
                )
            )
            exit()

    if preset:
        from shutil import copytree

        copytree(Path(__file__).parent.joinpath("preset"), path, dirs_exist_ok=True)
    else:
        path.joinpath("src/pages").mkdir(parents=True, exist_ok=True)
        path.joinpath("src/components").mkdir(parents=True, exist_ok=True)
        path.joinpath("public").mkdir(parents=True, exist_ok=True)

    CONFIG = build_config(".yml", {})
    CONFIG.site.name = name
    CONFIG.save(path.joinpath("moph.yml"))

    Logger.info(
        TED.parse(
            f"Finished! Next cd into [@Fyellow]{name!r}[@F] and use [@Fyellow]'moph build'"
        )
    )

@cli.command(name="serve")
@click.option("-o", "--open", flag_value=True, default=False, help="open the server in the browser")
@click.option("--host", flag_value=True, default=False, help="expose the network url for the server")
def serve(open: bool, host: bool):
    """Serve the site; when files change, rebuild the site and reload the server."""

    server = LiveServer(port=8081, open=open, expose_host=host)
    server.run()
    rmtree(states["dest"], ignore_errors=True)

@cli.command(name="preview")
@click.option("-o", "--open", flag_value=True, default=False, help="open the server in the browser")
@click.option("--host", flag_value=True, default=False, help="expose the network url for the server")
def preview(open: bool, host: bool):
    """Preview the project. This includes building to the websites root and launching a server.
    There are no live updates, to get that use `moph serve`.
    """

    full_build()
    server = Server(port=8081, open=open, expose_host=host)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    rmtree(states["dest"], ignore_errors=True)


if __name__ == "__main__":
    cli()