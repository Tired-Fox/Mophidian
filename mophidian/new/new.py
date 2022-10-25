import os
import sys
import contextlib
from json import dumps
from pathlib import Path
from typing import TextIO

from integration import Tailwindcss, Sass, check_nodejs
from moph_logger import Log, LL, color, Style, BColor, FColor

from .snippets import snippets


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

        check_nodejs()
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
                    sass_integration = Sass(logger, package_manager)
                    sass_integration.install()

                if tailwind:
                    tailwind_integration = Tailwindcss(logger, package_manager)
                    tailwind_integration.install()
                    config["build"]["refresh_delay"] = 3

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
