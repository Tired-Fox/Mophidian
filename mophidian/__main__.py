from pathlib import Path
from shutil import copytree, rmtree
from sys import stdout
import click
from saimll import SAIML, LogLevel, Logger
from watchserver import LiveServer
import mophidian
from mophidian.compile import Compiler
from mophidian.compile.serve import Callbacks, run_server
from mophidian.config import CONFIG
from mophidian.pygmentize import generate_highlight, print_styles

from beaupy import select, prompt

DEV = ".dev"
PREVIEW = "preview"
HELP = {
    "build": {
        "dirty": "Force write files even if the rendered file already exists",
        "no-scripts": "don't run pre build and post build scripts",
    },
    "preview": "Run a live reload server and build the website. The server auto reloads output file changes"
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
@click.option(
    "-l", "--list", flag_value=True, help="List Pygmentize styles", default=False
)
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
    name="build",
    help=f"Compile and build the website to {CONFIG.paths.out!r}",
)
def build(debug: bool, dirty: bool, no_scripts: bool = False):
    """Build the website in the specified output directory."""

    compiler = Compiler()

    if debug:
        Logger.level(LogLevel.DEBUG)

    compiler.build(dirty=dirty, scripts=not no_scripts)

    Logger.flush()


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
    "--no-scripts",
    flag_value=True,
    default=False,
    help="don't run pre build and post build scripts",
)
@click.option("-p", "--port", default=3031, help="run server on specified port")
@cli.command(name="dev")
def dev(
    open: bool,
    host: bool,
    debug: bool = False,
    no_scripts: bool = False,
    port: int = 3031,
):
    """Serve the site; when files change, rebuild the site and reload the server."""

    if debug:
        Logger.level(LogLevel.DEBUG)

    CONFIG.paths.out = DEV
    CONFIG.site.base = ""

    server = LiveServer(
        watch=[CONFIG.paths.files, CONFIG.paths.public, CONFIG.paths.components],
        root=DEV,
        errors=CONFIG.site.base,
        auto_open=CONFIG.site.base if open else None,
        suppress=True,
        port=port,
        live_callback=Callbacks(not no_scripts),
    )

    try:
        run_server(server, host)
    except Exception as exc:
        raise exc
    finally:
        rmtree(DEV, ignore_errors=True)

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
@cli.command(name="preview")
def preview(open: bool, host: bool, no_scripts: bool = False, port: int = 3031):
    """Preview the project as if it was deployed. This will serve the project with the configured website base.
    There are no live updates, to get that use `moph dev`. The server only reloads when output files
    are changed.
    """

    CONFIG.paths.out = f"{PREVIEW}/{CONFIG.site.base.strip('/')}"

    compiler = Compiler()
    server = LiveServer(
        watch=[f"{PREVIEW}/"],
        root=PREVIEW,
        errors=CONFIG.site.base,
        port=port,
        auto_open=CONFIG.site.base if open else None,
        suppress=True,
    )

    try:
        compiler.build(True, no_scripts)
        run_server(server, host)
    except Exception as exc:
        raise exc
    finally:
        rmtree(PREVIEW, ignore_errors=True)

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
    default="",
)
@cli.command(name="new", help="Create a new mophidian project")
def new(force: bool, preset: str, name: str):
    """Stylize markdown code blocks with pygmentize. This command allows you to generate the
    CSS file with a given styles highlight colors.
    """

    while name == "":
        name = prompt("Enter the name of your project: ", initial_value="app")
        print(SAIML.parse(f"[@Fyellow]name[@F]: *{name}"))

    path = Path(name.lower())

    if path.is_dir():
        if force:
            rmtree(path)
        else:
            Logger.Error(
                SAIML.parse(
                    f"Failed to create project [@Fyellow]/{name}[@F] since it already exists"
                )
            )
            exit()

    if preset == "":
        preset = select_preset()

    Logger.Info("Generating file structure")
    copytree(
        Path(__file__).parent.joinpath(f"presets/{preset}"), path, dirs_exist_ok=True
    )

    CONFIG.site.name = name
    CONFIG.save((path / "moph.yml").as_posix())

    Logger.Info(
        SAIML.parse(
            f"Finished! Next cd into [@Fyellow]{name!r}[@F] and start building"
        )
    )

PRESETS = {
    "basic": "Basic website sample using navigation and components",
    "blank": "A basic mophidian file structure to help get things started"
}

def select_preset() -> str:
    message = "Select a preset:"
    presets = [preset.stem for preset in Path(__file__).parent.joinpath(f"presets/").glob("*") if preset.is_dir()]

    print(message)
    with_desc = lambda x: f"{x}: {PRESETS[x]}" 
    preset = select(presets, cursor=">", preprocessor=lambda x: with_desc(x) if x in PRESETS else x)

    # Remove the prompt from the selector above
    stdout.write("\x1b[1A\x1b[1M")
    stdout.flush()

    # Output the selected preset
    print(f"{SAIML.parse(f'[@Fyellow]preset[@F]: *{preset}')}")

    return preset 

if __name__ == "__main__":
    cli()
