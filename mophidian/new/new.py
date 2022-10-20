import contextlib
from json import dumps
from msilib import FCICreate
import os
from pathlib import Path
import sys
from typing import TextIO

from .snippets import snippets
from moph_logger import Log, LL, color, Style, BColor, FColor


def add_sass_scripts(logger: Log):
    logger.Info("Adding sass scripts to package.json")
    logger.Debug(f"Added\n{snippets['sass_scripts']}")
    with open("./package.json", "r", encoding="utf-8") as package_json:
        from json import load, dumps

        pj = load(package_json)
        if "scripts" not in pj:
            pj["scripts"] = {}
        pj["scripts"].update(snippets["sass_scripts"])

    with open("./package.json", "w", encoding="utf-8") as package_json:
        package_json.write(dumps(pj, indent=2))


def add_tailwind_scripts():
    with open("./package.json", "r", encoding="utf-8") as package_json:
        from json import load, dumps

        pj = load(package_json)
        if "scripts" not in pj:
            pj["scripts"] = {}

        pj["scripts"].update(snippets["tailwind_scripts"])

    with open("./package.json", "w", encoding="utf-8") as package_json:
        package_json.write(dumps(pj, indent=2))


def add_tailwind_css():
    Path("styles").mkdir(parents=True, exist_ok=True)
    with open("styles/tailwind.css", "+w", encoding="utf-8") as tailwindcss:
        tailwindcss.write(snippets["tailwind_css"])


def add_tailwind_config():
    with open("tailwind.config.js", "+w", encoding="utf-8") as tcss_cfg:
        tcss_cfg.write(snippets["tailwind_config"])


def add_tailwind(logger: Log):
    logger.Info("Adding tailwindcss scripts to package.json")
    logger.Debug(f"Added\n{snippets['tailwind_scripts']}")
    add_tailwind_scripts()
    logger.Info("Generating tailwind.css file in styles/")
    logger.Debug(f"Generated tailwind.css with:\n{snippets['tailwind_css']}")
    add_tailwind_css()
    logger.Info("Generating tailwindcss config")
    logger.Debug(f"Generated tailwind.config.js with:\n{snippets['tailwind_config']}")
    add_tailwind_config()


def create_config(config: dict):
    with open("moph.json", "+w", encoding="utf-8") as cfg:
        from json import dumps

        cfg.write(dumps(config, indent=2))


def setup(
    name: str,
    version: str,
    sass: bool,
    tailwind: bool,
    no_defaults: bool,
    logger: Log,
    old_out: TextIO,
    old_err: TextIO,
    **kwargs,
):
    config = {
        "site": {"name": name, "version": version},
        "build": {"refresh_delay": 0.3},
        "markdown": {"append": no_defaults, "extensions": [], "extension_configs": {}},
        "integration": {
            "sass": sass,
            "tailwind": tailwind,
        },
    }

    from shutil import which
    from ppm import PPM

    package_manager = PPM(logger=logger)

    if sass or tailwind:
        logger.Info("Detected integration flags checking for node...")
        if which("node") is not None:
            import subprocess

            logger.Info(f"Node {subprocess.check_output(['node', '--version']).decode()}")

            with contextlib.redirect_stdout(old_out):
                with contextlib.redirect_stderr(old_err):
                    while True:
                        ppm = input(
                            f"Which node package manager whould you like to use?\n\
{', '.join(package_manager.names)}: "
                        )
                        if package_manager.is_valid(ppm.lower()):
                            config["integration"]["package_manager"] = ppm.lower()
                            break

            package_manager.ppm.init()

            if sass:
                package_manager.ppm.install("sass", "-D")
                add_sass_scripts(logger=logger)

            if tailwind:
                package_manager.ppm.install("tailwindcss", "-D")
                add_tailwind(logger=logger)
                config["build"]["refresh_delay"] = 3

        else:
            logger.Error(
                "Node is not installed. It must be installed to use integrations.\n Check out <link goes here> to find out more."
            )

    logger.Info("Generating mophidian config")
    logger.Debug(f"\n{color(dumps(config, indent=2), prefix=[Style.BOLD], suffix=[Style.NOBOLD])}")

    create_config(config)

    logger.Info("Generating files and directories")

    logger.Debug("Creating this file structure")
    if tailwind or sass:
        logger.Debug(snippets["integration_file_structure"])
    else:
        logger.Debug(snippets["base_file_structure"])

    dirs = [Path("content"), Path("components"), Path("layouts"), Path("pages"), Path("static")]
    for dir in dirs:
        dir.mkdir(parents=True, exist_ok=True)

    with open("pages/index.html", "+w", encoding="utf-8") as starter_index:
        starter_index.write(snippets["starter_index"])


def generate(**kwargs):
    name = input("Site Name: ")
    version = input("Version {1.0}: ")
    if version == "":
        version = "1.0"

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    log_level = LL.INFO
    if kwargs["debug"]:
        log_level = LL.DEBUG

    with contextlib.redirect_stdout(None):
        with contextlib.redirect_stderr(None):
            logger = Log(level=log_level, output=old_stdout)

            # Make dir if not already there
            new_project = Path(name)
            if os.path.isdir(new_project):
                logger.Error(f"{name} already exists!")
                exit(2)

            new_project.mkdir(parents=True, exist_ok=True)
            os.chdir(name)

            setup(
                name=name,
                version=version,
                logger=logger,
                old_out=old_stdout,
                old_err=old_stderr,
                **kwargs,
            )
            logger.Success(
                "run ",
                color("cd ", prefix=[FColor.YELLOW]),
                color(f"./{name}", prefix=[FColor.CYAN]),
                " and ",
                color(f"mophidian serve", prefix=[FColor.CYAN]),
                ("[" + color(f"-o", prefix=[FColor.CYAN]) + "]"),
                " to get started",
            )
