#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
from shutil import rmtree, copytree
import socket
from time import sleep
import click

from watchserver import LiveServer
from saimll import SAIML, Logger, LogLevel, style

from mophidian.old import STATE, DestState, __version__
from mophidian.old.cli.styles import generate_highlight
from mophidian.old.config import CONFIG
from mophidian.old.core import (
    build as full_build,
    Callbacks,
)


def server_start(server: LiveServer, expose: bool = False):
    """Start a server and print the started message with hosts."""
    # Get port and network information
    socket_server = server.server_thread.server
    IPHostName = socket.gethostname()

    url = socket_server.url()
    network_ip = socket_server.url(socket.gethostbyname(IPHostName))
    network_host_name = socket_server.url(IPHostName)

    network_message = f"use {style('--host', fg='yellow')} to expose"
    if expose:
        network_message = (
            f"{SAIML.parse(f'[@Fyellow~{network_ip}]{network_ip}')}\n"
            + f"{' '*17}{SAIML.parse(f'[@Fyellow~{network_host_name}]{network_host_name}')}"
        )

    # Start server and print started message
    server.start()
    (
        Logger.custom(
            style("Mophidian", fg="white", bg=(166, 218, 149)),
            "server has started",
            label="🚀",
            clr="white",
        )
        .message()
        .message(
            f"{' '*6}▍ {style('Local', fg='cyan')}:   {SAIML.parse(f'[@Fyellow~{url}]{url}')}"
        )
        .message(f"{' '*6}▍ {style('Network', fg='cyan')}: {network_message}")
        .Message()
    )


def server_shutdown(server: LiveServer):
    """Shutdown a server and print the shutdown message."""
    Logger.Custom(
        style("Mophidian", fg="white", bg=(166, 218, 149)),
        "Shutting down...",
        label="🚀",
        clr="white",
    )
    server.stop()


def run_server(server: LiveServer, expose: bool = False):
    """Run a live reloading server."""

    try:
        server_start(server, expose)
        while True:
            sleep(1)
    except KeyboardInterrupt:
        server_shutdown(server)


@click.group(invoke_without_command=True)
@click.option(
    "-v", "--version", flag_value=True, help="Version of mophidian", default=False
)
def cli(version: bool = False):
    """Pythonic Static Site Generator CLI."""

    if version:
        click.echo(f"Mophidian v{__version__}")
        exit()


@click.option("--debug", flag_value=True, help="Enable debug logs", default=False)
@click.option(
    "--dirty",
    flag_value=True,
    help="Force write files even if the rendered file already exists",
    default=False,
)
@click.option(
    "--no-scripts",
    flag_value=True,
    default=False,
    help="don't run pre build and post build scripts",
)
@cli.command(
    name="build", help=f"Compile and build the website to {CONFIG.site.dest!r}"
)
def build_command(debug: bool, dirty: bool, no_scripts: bool = False):
    """Build the website in the specified dest directory."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    if dirty:
        rmtree("out/")

    STATE.dest = DestState.FINAL
    Logger.Custom("Building website...", label="▮", clr="cyan")
    full_build(dirty=dirty, scripts=not no_scripts)

    Logger.flush()


@click.argument("style", default="")
@cli.command(name="highlight", help="Generate a pygmentize CSS file")
def code_highlight(style: str):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """
    generate_highlight(style)


@click.argument("name", default="")
@click.option(
    "-f",
    "--force",
    flag_value=True,
    help="force write files and directories even if they already exist",
    default=False,
)
@click.option(
    "-p",
    "--preset",
    help="generate the project with a preset",
    default="default",
)
@cli.command(name="new", help="Create a new mophidian project")
def new(force: bool, preset: bool, name: str):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """

    while name == "":
        name = input("Enter the name of your project: ")

    Logger.Info("Generating file structure")

    path = Path(name.lower())

    if path.is_dir():
        if force:
            rmtree(path)
        else:
            Logger.error(
                SAIML.parse(
                    f"Failed to create project [@Fyellow]/{name}[@F] since it already exists"
                )
            )
            exit()

    copytree(
        Path(__file__).parent.joinpath(f"preset/{preset}"), path, dirs_exist_ok=True
    )

    CONFIG.site.name = name
    CONFIG.save((path / "moph.yml").as_posix())

    Logger.info(
        SAIML.parse(
            f"Finished! Next cd into [@Fyellow]{name!r}[@F] and use [@Fyellow]'moph build'"
        )
    )


@click.option(
    "-o",
    "--open",
    flag_value=True,
    default=False,
    help="open the server in the browser",
)
@click.option(
    "-d",
    "--debug",
    flag_value=True,
    default=False,
    help="set logging level to debug",
)
@click.option(
    "--host",
    flag_value=True,
    default=False,
    help="expose the network url for the server",
)
@click.option(
    "--host",
    flag_value=True,
    default=False,
    help="expose the network url for the server",
)
@click.option(
    "--no-scripts",
    flag_value=True,
    default=False,
    help="don't run pre build and post build scripts",
)
@click.option(
    "-p",
    "--port",
    default=3031,
    help="run server on specified port"
)
@cli.command(name="dev")
def dev(open: bool, host: bool, debug: bool = False, no_scripts: bool = False, port: int = 3031):
    """Serve the site; when files change, rebuild the site and reload the server."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    STATE.dest = DestState.DEV
    server = LiveServer(
        watch=[CONFIG.site.source, CONFIG.site.public, CONFIG.site.components],
        root="_dev",
        errors=CONFIG.site.root,
        auto_open=CONFIG.site.root if open else None,
        suppress=True,
        port=port,
        live_callback=Callbacks(not no_scripts),
    )

    try:
        run_server(server, host)
    except Exception as exc:
        raise exc
    finally:
        rmtree("_dev", ignore_errors=True)


@cli.command(name="preview")
@click.option(
    "-o",
    "--open",
    flag_value=True,
    default=False,
    help="open the server in the browser",
)
@click.option(
    "--host",
    flag_value=True,
    default=False,
    help="expose the network url for the server",
)
@click.option(
    "--no-scripts",
    flag_value=True,
    default=False,
    help="don't run pre build and post build scripts",
)
@click.option(
    "-p",
    "--port",
    default=3031,
    help="run server on specified port"
)
def preview(open: bool, host: bool, no_scripts: bool = False, port: int = 3031):
    """Preview the project. This includes building to the websites root and launching a server.
    There are no live updates, to get that use `moph serve`.
    """

    STATE.dest = DestState.PREVIEW
    server = LiveServer(
        watch=["_preview/"],
        root="_preview",
        errors=CONFIG.site.root,
        port=port,
        auto_open=CONFIG.site.root if open else None,
        suppress=True,
    )

    try:
        full_build(True, no_scripts)

        run_server(server, host)
    except Exception as exc:
        raise exc
    finally:
        rmtree("_preview", ignore_errors=True)


if __name__ == "__main__":
    cli()
