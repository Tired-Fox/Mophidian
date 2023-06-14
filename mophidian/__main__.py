from shutil import rmtree
import click
from saimll import LogLevel, Logger
import mophidian
from mophidian.compile import Compiler
from mophidian.pygmentize import generate_highlight, print_styles

HELP = {
    "build": {
        "dirty": "Force write files even if the rendered file already exists",
        "no-scripts": "don't run pre build and post build scripts"
    },
}

@click.group(invoke_without_command=True)
@click.option(
    "-v", "--version", flag_value=True, help="Version of mophidian", default=False
)
def cli(version: bool = False):
    """Pythonic Static Site Generator CLI."""

    if version:
        click.echo(f"Mophidian v{mophidian.__version__}")
        exit()

@click.argument("style", default="")
@click.option("-l", "--list", flag_value=True, help="List Pygmentize styles", default=False)
@cli.command(name="highlight", help=f"Generate a pygmentize CSS file")
def code_highlight(style: str, list: bool = False):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """
    # PERF: Update cli too to be interactive and searchable
    if list:
        print_styles()
    else:
        generate_highlight(style)

@click.option("--debug", flag_value=True, help="Enable debug logs", default=False)
@click.option(
    "--dirty",
    flag_value=True,
    help=HELP["build"]["dirty"],
    default=False,
)
@click.option(
    "--no-scripts",
    flag_value=True,
    default=False,
    help=HELP["build"]["no-scripts"],
)
@cli.command(
    name="build", help=f"Compile and build the website to {mophidian.CONFIG.paths.out!r}"
)
def build_command(debug: bool, dirty: bool, no_scripts: bool = False):
    """Build the website in the specified dest directory."""

    compiler = Compiler()

    if debug:
        Logger.level(LogLevel.DEBUG)

    rmtree("out/")

    compiler.build(dirty=dirty, scripts=not no_scripts)

    Logger.flush()

if __name__ == "__main__":
    cli()
