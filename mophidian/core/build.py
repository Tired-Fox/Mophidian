from pathlib import Path
from shutil import rmtree
from os import remove

from phml import PHML
from teddecor import TED, Logger

from mophidian import CONFIG, states
from mophidian.FileSystem import (
    Directory,
    Component,
    Static,
    Layout,
    Page,
    Markdown,
    Nav,
    FileState,  
    REGEX,
    PAGE_IGNORE,
    title,
    url
)
from .context import Mophidian, MOPHIDIAN_TYPES

__all__ = [
    "render_pages",
    "write_static_files",
    "build"
]

def construct_components(path: str) -> Directory:
    """Find all the components in the given path and construct a file structure."""

    components = Directory(path)
    for file in Path(path).glob("**/*.*"):
        if file.suffix == ".phml":
            components.add(Component(file.as_posix(), path))
        else:
            suggestion = f"{TED.parse(f'[@Fred]{file.suffix}')} to {TED.parse('[@Fgreen].phml')}"
            Logger.Debug(
                "Invalid component:",
                f"{TED.parse(f'[@Fyellow]{TED.escape(file.as_posix())}')}.",
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

def render_pages(
    root: Directory,
    static_files: Directory,
    component_files: Directory,
    out: str,
    phml: PHML,
    nav: Nav = Nav(""),
    dirty: bool = False
):
    """Render all the pages with their layouts to their destination file."""

    global_vars = {
        "url": url,
        "title_case": title,
        "nav": nav,
    }

    # Render pages
    for page in root.renderable():
        if page.state == FileState.UPDATED or (dirty and page.state != FileState.DELETED):
            page_vars = {
                "title": page.title
            }

            # Ensure path to file
            page.dest(out).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            dest = Path(page.dest(out))
            output = page.render(
                phml,
                page_files=root,
                static_files=static_files,
                component_files=component_files,
                **page_vars,
                **global_vars
            )

            with open(dest, "+w", encoding="utf-8") as file:
                file.write(output)
            page.state = FileState.NULL
        elif page.state == FileState.DELETED:
            dest = Path(page.dest(out))
            root.remove(page.full_path)
            page.delete()
            if len(list(dest.parent.glob("**/*.*"))) == 1:
                rmtree(dest.parent)
            elif dest.is_file():
                remove(dest)

def write_static_files(root: Directory, static: Directory, out: str):
    """Write static files to their destination."""

    # static files found in the pages directory
    for file in root.static():
        if file.state == FileState.UPDATED:
            file.write(out)
        elif file.state == FileState.DELETED:
            dest = file.dest(out)
            root.remove(file.full_path)
            if len(list(dest.parent.glob("**/*.*"))) == 1:
                rmtree(dest.parent)
            else:
                remove(dest)

    # static files in the static directory
    for file in static.static():
        if file.state == FileState.UPDATED:
            file.write(out)
        elif file.state == FileState.DELETED:
            dest = file.dest(out)
            static.remove(file.full_path)
            if len(list(dest.parent.glob("**/*.*"))) == 1:
                rmtree(dest.parent)
            else:
                remove(dest)

def build(display_files: bool = False):
    """Take the components and files and render and write them to the given output directory."""

    Logger.Debug("Building pages")

    #? Init phml parser/compiler with globally exposed variables
    phml = PHML()
    phml.expose(mophidian=Mophidian(), **MOPHIDIAN_TYPES)

    Logger.Debug("Discovering files and components")

    #? Discover all files and build nav
    components = construct_components(CONFIG.site.components)
    file_system, nav = construct_file_system(CONFIG.site.source)
    public = construct_static(CONFIG.site.public)

    #? Add components to phml compiler
    phml.add(
        *[(cmpt.cname, cmpt.full_path) for cmpt in components.components()],
        strip=CONFIG.site.components
    ) # type: ignore

    if display_files:
        Logger.custom(
            f"({len(file_system)}) files found", label="File System", clr="178"
        ).Message(file_system)

    #? Render all the pages
    dest = states["dest"]
    Logger.Debug(f"Rendering pages to {TED.parse(f'[@F yellow $]{dest}')}")

    render_pages(file_system, public, components, nav=nav, out=dest, phml=phml)
    write_static_files(file_system, public, out=dest)

    Logger.Debug("Finished building pages")
    return file_system, public, components, phml