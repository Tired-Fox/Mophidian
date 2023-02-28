#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
from shutil import rmtree
import socket
from time import sleep
import click

from watchserver import LiveServer
from saimll import SAIML, Logger, LogLevel, style

from mophidian import states, DestState, __version__
from mophidian.cli.styles import generate_highlight
from mophidian.config import CONFIG
from mophidian.core import (
    build as full_build,
    generate_sitemaps,
    generate_rss,
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
@cli.command(
    name="build", help=f"Compile and build the website to {CONFIG.site.dest!r}"
)
def build_command(debug: bool, dirty: bool):
    """Build the website in the specified dest directory."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    if dirty:
        rmtree("out/")

    states["dest"] = DestState.PREVIEW
    file_system, _, _, _ = full_build(dirty=dirty)

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
    flag_value=True,
    help="generate the project with a preset",
    default=False,
)
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
                SAIML.parse(
                    f"Failed to create project [@Fyellow]/{name}[@F] since it already exists"
                )
            )
            exit()

    if preset:
        from shutil import copytree

        copytree(
            Path(__file__).parent.joinpath("preset/default"), path, dirs_exist_ok=True
        )
    else:
        path.joinpath("src/pages").mkdir(parents=True, exist_ok=True)
        path.joinpath("src/components").mkdir(parents=True, exist_ok=True)
        path.joinpath("public").mkdir(parents=True, exist_ok=True)

    CONFIG.site.name = name
    CONFIG.save()

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
@cli.command(name="dev")
def dev(open: bool, host: bool, debug: bool = False):
    """Serve the site; when files change, rebuild the site and reload the server."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    server = LiveServer(
        watch=[CONFIG.site.source, CONFIG.site.public, CONFIG.site.components],
        root="dist",
        base=CONFIG.site.root,
        auto_open=open,
        suppress=True,
        live_callback=Callbacks(),
    )

    run_server(server, host)
    rmtree("dist", ignore_errors=True)


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
def preview(open: bool, host: bool):
    """Preview the project. This includes building to the websites root and launching a server.
    There are no live updates, to get that use `moph serve`.
    """

    server = LiveServer(
        watch=["dist/"],
        root="dist",
        base=CONFIG.site.root,
        port=8081,
        auto_open=open,
        suppress=True,
    )

    run_server(server, host)
    rmtree("dist", ignore_errors=True)


if __name__ == "__main__":
    cli()
