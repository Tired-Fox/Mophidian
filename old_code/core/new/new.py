import os
import shutil
import sys
import contextlib
from json import dumps
from pathlib import Path
from typing import TextIO

from mophidian.core.integration import Tailwindcss, Sass
from mophidian.moph_log import Logger, color, FColor, Style

from mophidian.core.snippets import snippets
from mophidian.core.ppm import PPM


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
    config: dict,
    ostdo: TextIO,
    ostde: TextIO,
    **kwargs,
):
    if config is None:
        config = {
            "site": {"name": name, "version": version},
            "build": {"refresh_delay": 0.3},
            "markdown": {"append": not no_defaults, "extensions": [], "extension_configs": {}},
            "integration": {
                "sass": sass,
                "tailwind": tailwind,
            },
        }
    else:
        config["site"]["name"] = name
        config["site"]["version"] = version
        config["integration"]["sass"] = sass
        config["integration"]["tailwind"] = tailwind

    package_manager = PPM(logger=Logger)

    if sass or tailwind:
        Logger.Info("Detected integration flags checking for node...")
        with contextlib.redirect_stdout(ostdo):
            with contextlib.redirect_stderr(ostde):
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
                    sass_integration = Sass(Logger, package_manager)
                    sass_integration.install(config)

                if tailwind:
                    tailwind_integration = Tailwindcss(Logger, package_manager)
                    tailwind_integration.install()
                    config["build"]["refresh_delay"] = 3

    Logger.Info("Generating mophidian config")
    Logger.Debug(f"\n{color(dumps(config, indent=2), prefix=[Style.BOLD], suffix=[Style.NOBOLD])}")

    create_config(config)

    Logger.Info("Generating files and directories")

    Logger.Debug("Creating this file structure")
    if tailwind or sass:
        Logger.Debug(snippets["integration_file_structure"])
    else:
        Logger.Debug(snippets["base_file_structure"])

    dirs = [Path("content"), Path("components"), Path("layouts"), Path("pages"), Path("static")]
    for dir in dirs:
        dir.mkdir(parents=True, exist_ok=True)


def generate(**kwargs):
    name = input("Site Name: ")
    version = input("Version {1.0}: ")
    if version == "":
        version = "1.0"

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    with contextlib.redirect_stdout(None):
        with contextlib.redirect_stderr(None):
            # Make dir if not already there
            new_project = Path(name)
            if os.path.isdir(new_project):
                Logger.Error(f"{name} already exists!")
                exit(2)

            if kwargs["template"] not in ["blank"]:
                kwargs["template"] = "blank"

            template_path = Path(__file__).parent.parent.parent.joinpath(
                f"templates/{kwargs['template']}"
            )

            if template_path.joinpath("moph.json").exists():
                with open(template_path.joinpath("moph.json"), "r", encoding="utf-8") as cfg:
                    from json import load

                    config = load(cfg)
            else:
                config = None

            shutil.copytree(
                template_path,
                new_project,
            )

            os.chdir(name)

            setup(
                name=name,
                version=version,
                logger=Logger,
                ostdo=old_stdout,
                ostde=old_stderr,
                config=config,
                **kwargs,
            )
            Logger.Success(
                "run ",
                color("cd ", prefix=[FColor.YELLOW]),
                color(f"./{name}", prefix=[FColor.CYAN]),
                " and ",
                color(f"mophidian serve", prefix=[FColor.CYAN]),
                ("[" + color(f"-o", prefix=[FColor.CYAN]) + "]"),
                " to get started",
            )
