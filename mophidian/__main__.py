#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import click
from shutil import rmtree

from teddecor import Logger, LL, TED

from mophidian.FileSystem import build as full_build
from mophidian.config import CONFIG, build_config


@click.group()
def cli():
    '''Pythonic Static Site Generator CLI.'''

@click.option("-d", "--debug", flag_value=True, help="Enable debug logs", default=False)
@click.option("-f", "--files", flag_value=True, help="Log the files that were found in the build process", default=False)
@cli.command(name="build", help=f"Compile and build the website to {CONFIG.site.dest!r}")
def build_command(debug: bool, files: bool):
    """Build the website in the specified dest directory."""

    if debug:
        Logger.level(LL.DEBUG)

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

    Logger.info("Generating file strucutre").flush()

    path = Path(name.lower())

    if path.is_dir():
        if force:
            rmtree(path)
        else:
            Logger.error(
                TED.parse(
                    f"Failed to create project [@Fyellow]/{name}[@F] since it already exists"
                )
            ).flush()
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

    Logger.success(
        TED.parse(
            f"Next cd into [@Fyellow]{name!r}[@F] and use [@Fyellow]'moph build'"
        )
    ).flush()


if __name__ == "__main__":
    cli()

# @cli.command(name="serve")
# @click.option("-o", "--open", flag_value=True, help=open_help, default=False)
# def serve_command(open: bool):
#     """Start a live reload server that auto builds and reloads on file changes.

#     Args:
#         open (bool): Whether to open in the default browser automatically.
#     """
#     import livereload

#     # Init server and builder
#     server = livereload.Server()
#     builder = Builder(logger=Logger)

#     # Change source dir to be source + website root for proper links
#     CONFIG.site.dest = ".dist/"
#     old_dest = CONFIG.site.dest
#     CONFIG.site.dest = CONFIG.site.dest + CONFIG.site.root

#     # Full build before deploy
#     builder.full()

#     def rebuild(dirty: bool = False):
#         builder.rebuild(dirty)

#     # Watch pages, content, and static
#     server.watch(
#         filepath=CONFIG.site.source,
#         func=lambda: rebuild(True),
#         delay="forever",
#     )
#     server.watch(
#         filepath=CONFIG.site.content,
#         func=lambda: rebuild(True),
#         delay="forever",
#     )

#     server.watch(
#         filepath="components/",
#         func=rebuild,
#         delay="forever",
#     )

#     server.watch(
#         filepath="layouts/",
#         func=rebuild,
#         delay="forever",
#     )

#     server.watch(
#         filepath="static/",
#         func=lambda: builder.copy_all_static_dir(dirty=True),
#         delay="forever",
#     )

#     server.watch(filepath=CONFIG.site.dest)

#     # TODO start sass and tailwind watch commands
#     Logger.Message("\n\n")

#     Logger.Custom(f"Serving to http://localhost:3000/", label="Serve", clr="yellow")
#     try:
#         with contextlib.redirect_stdout(None):
#             with contextlib.redirect_stderr(None):
#                 server.serve(
#                     port=3000,
#                     root=f"{old_dest}",
#                     open_url_delay=0.3 if open else None,
#                     live_css=True,
#                     restart_delay=2,
#                 )
#     finally:
#         Logger.Custom("Shutting down...", label="Shutdown")
#         builder.del_dest(old_dest)



