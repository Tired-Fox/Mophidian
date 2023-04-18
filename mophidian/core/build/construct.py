from re import match
from pathlib import Path
import time

from saimll import SAIML, Logger
from phml import HypertextManager

from mophidian import CONFIG
from mophidian.file_system import Directory, Component, Nav, Static, Layout, Page, Markdown, Renderable
from mophidian.core.util import REGEX, PAGE_IGNORE
from datetime import datetime

__all__ = [
    "construct_components",
    "construct_static",
    "construct_file_system",
]

def construct_components(path: str) -> Directory:
    """Find all the components in the given path and construct a file structure."""

    components = Directory(path)
    for file in Path(path).glob("**/*.*"):
        if file.suffix == ".phml":
            components.add(Component(file.as_posix(), path))
        else:
            suggestion = f"{SAIML.parse(f'[@Fred]{file.suffix}')} to {SAIML.parse('[@Fgreen].phml')}"
            Logger.Debug(
                "Invalid component:",
                f"{SAIML.parse(f'[@Fyellow]{SAIML.escape(file.as_posix())}')}.",
                "Try changing",
                suggestion,
                label="Debug.[@Fred]Error[@]"
            )
    return components

def construct_static(path: str) -> Directory:
    """Find all the static files in the given path and construct a file structure."""

    static_files = Directory(path)
    for file in Path(path).glob("**/*.*"):
        static_files.add(Static(file.as_posix(), path))

    return static_files

def construct_file_system(path: str) -> tuple[Directory, Nav]:
    """Find all the files in the given path and construct a file structure."""

    Logger.Debug("Generating file system from path:", path.lstrip('/'))
    root = Directory(path)
    for _file in Path(path).glob("**/*.*"):
        # Pages and Layouts
        if _file.suffix == ".phml":
            if REGEX["layout"]["name"].match(_file.name) is not None:
                root.add(Layout(_file.as_posix(), path))
            elif REGEX["page"]["name"].match(_file.name) is not None:
                root.add(Page(_file.as_posix(), path))
            else:
                file_info = REGEX["file"]["name"].search(_file.name)
                file_name, _, _, _ = (
                    file_info.groups() if file_info is not None else ("", None, None, "")
                )
                if file_name in PAGE_IGNORE:
                    root.add(Page(_file.as_posix(), path))

        # Markdown files
        elif _file.suffix in [".md", ".mdx"]:
            root.add(Markdown(_file.as_posix(), path))

        # Static files
        else:
            root.add(Static(_file.as_posix(), path))

    root.build_hierarchy()
    nav = root.build_nav()
    return root, nav

