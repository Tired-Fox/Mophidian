from genericpath import isdir
import os
from pathlib import Path
from textwrap import indent
from tkinter.font import BOLD
from .snippets import snippets
from util import color, Color, Style, RESET


def add_sass_scripts():
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


def add_tailwind():
    add_tailwind_scripts()
    add_tailwind_css()
    add_tailwind_config()


def create_config(config: dict):
    with open("moph.json", "+w", encoding="utf-8") as cfg:
        from json import dumps

        cfg.write(dumps(config, indent=2))


def setup(name: str, version: str, sass: bool, tailwind: bool, no_defaults: bool, **kwargs):
    config = {
        "site": {"name": name, "version": version},
        "build": {},
        "markdown": {"append": no_defaults, "extensions": [], "extension_configs": {}},
        "integration": {
            "sass": sass,
            "tailwind": tailwind,
        },
    }

    from shutil import which
    from ppm import PPM

    package_manager = PPM()

    if sass or tailwind:
        print(f"Detected integration flags checking for node...")
        if which("node") is not None:
            import subprocess

            print(
                color(
                    "[",
                    color("INFO", prefix=[Color.CYAN]),
                    "] Node ",
                    subprocess.check_output(['node', '--version']).decode(),
                    prefix=[Color.YELLOW],
                )
            )

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
                add_sass_scripts()

            if tailwind:
                package_manager.ppm.install("tailwindcss", "-D")
                add_tailwind()

        else:
            print(
                color(
                    "[",
                    color("WARNING", prefix=[Color.YELLOW]),
                    "] Node is not installed. It must be installed to use integrations.\n Check out <link goes here> to find out more.",
                    prefix=[Style.BOLD],
                    suffix=[RESET],
                )
            )

    create_config(config)
    dirs = [Path("content"), Path("components"), Path("layouts"), Path("pages"), Path("static")]
    for dir in dirs:
        dir.mkdir(parents=True, exist_ok=True)


def generate(**kwargs):
    name = input("Site Name: ")
    version = input("Version {1.0}: ")
    if version == "":
        version = "1.0"

    # Make dir if not already there
    new_project = Path(name)
    if os.path.isdir(new_project):
        print(
            color(
                "[",
                color("WARNING", prefix=[Color.YELLOW]),
                f"] {name} already exists!\n",
                "[",
                color("INFO", prefix=[Color.CYAN]),
                f"] Nothing will be overwritten, but any missing elements will be added.",
                prefix=[Style.BOLD],
                suffix=[RESET],
            )
        )
        print(f"Nothing will be overwritten, but any missing elements will be added.")
        exit(2)

    new_project.mkdir(parents=True, exist_ok=True)
    os.chdir(name)

    setup(name=name, version=version, **kwargs)
    print(
        color(
            "[",
            color("SUCCESS", prefix=[Color.GREEN]),
            f"] Created new project {name}!",
            prefix=[Style.BOLD],
            suffix=[RESET],
        )
    )
