#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import click
from shutil import rmtree

from teddecor import TED, Logger, LogLevel

from mophidian import states, DestState
from mophidian.cli.styles import generate_highlight
from mophidian.config import CONFIG, build_config
from mophidian.core import (
    Server,
    LiveServer,
    build as full_build,
    generate_sitemaps,
    generate_rss
)


@click.group()
def cli():
    '''Pythonic Static Site Generator CLI.'''

@click.option("--debug", flag_value=True, help="Enable debug logs", default=False)
@click.option(
    "--dirty",
    flag_value=True,
    help="Force write files even if the rendered file already exists",
    default=False
)
@cli.command(name="build", help=f"Compile and build the website to {CONFIG.site.dest!r}")
def build_command(debug: bool, dirty: bool):
    """Build the website in the specified dest directory."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    if dirty:
        rmtree("out/")

    states["dest"] = DestState.PREVIEW
    file_system, static, _, _ = full_build(dirty=dirty)

    if CONFIG.build.sitemap.enabled:
        generate_sitemaps(file_system)
        
    if CONFIG.build.rss.enabled:
        generate_rss(file_system)

    Logger.flush()

@click.argument("style", default="")
@cli.command(name="highlight", help="Generate a pygmentize CSS file")
def code_highlight(style: str):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """
    generate_highlight(style)

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

        copytree(Path(__file__).parent.joinpath("preset/default"), path, dirs_exist_ok=True)
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