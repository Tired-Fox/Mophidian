from pathlib import Path
from re import search

from teddecor import Logger, TED
from phml import PHML

from mophidian.core import Mophidian, MOPHIDIAN_TYPES
from mophidian.config import CONFIG

from .nodes import (
    Directory,
    Page,
    Layout,
    Component,
    Static,
    Markdown,
    Nav,
)
from .nodes.util import REGEX, PAGE_IGNORE, title, url

def build_components(path: str) -> Directory:
    """Find all the components in the given path and construct a file structure."""

    components = Directory(path)
    for file in Path(path).glob("**/*.*"):
        if file.suffix == ".phml":
            components.add(Component(file.as_posix(), path))
        else:
            suggestion = f"{TED.parse(f'[@Fred]{file.suffix}')} to {TED.parse('[@Fgreen].phml')}"
            Logger.debug(
                "Invalid component:",
                f"{TED.parse(f'[@Fyellow]{TED.escape(file.as_posix())}')}.",
                "Try changing",
                suggestion,
                label="Debug.[@Fred]Error[@]"
            )
    Logger.flush()
    return components

def build_static(path: str) -> Directory:
    """Find all the static files in the given path and construct a file structure."""

    static_files = Directory(path)
    for file in Path(path).glob("**/*.*"):
        static_files.add(Static(file.as_posix(), path))

    return static_files

def build_files(path: str) -> tuple[Directory, Nav]:
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
        elif _file.suffix == ".md":
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
            **page_vars,
            **global_vars
        )
        
        for link in ["href", "src"]:
            match = search("{link}=\"\/(?!{root})([^\"]*)\"|{link}='\/(?!{root})([^']*)'|\
{link}=\/(?!{root})([^\s<>\"']+)".format(link=link, root=CONFIG.site.root), output)
            while match is not None:
                rel = match.group(1)
                if rel is None:
                    rel = match.group(2)
                if rel is None:
                    rel = match.group(3)
                result = f'{link}="/{Path(CONFIG.site.root).joinpath(rel).as_posix()}\
{"/" if rel == "" else ""}"'
                output = (
                    output[:match.start()]
                    + result
                    + output[match.start() + len(match.group(0)):]
                )
                match = search("{link}=\"\/(?!{root})([^\"]*)\"|{link}='\/(?!{root})([^']*)'|\
{link}=\/(?!{root})([^\s<>\"']+)".format(link=link, root=CONFIG.site.root), output)

        with open(dest, "+w", encoding="utf-8") as file:
            file.write(output)

def write_static_files(root: Directory, static: Directory, out: str):
    """Write static files to their destination."""

    # static files found in the pages directory
    for file in root.static():
        file.write(out)

    # static files in the static directory
    for file in static.static():
        file.write(out)

def build(display_files: bool = False):
    """Take the components and files and render and write them to the given output directory."""

    Logger.info("Building pages").flush()
    phml = PHML()
    phml.expose(mophidian=Mophidian(), **MOPHIDIAN_TYPES)

    # Build components and files
    Logger.debug("Discovering files and components").flush()
    components = build_components(CONFIG.site.components)
    root, nav = build_files(CONFIG.site.source)
    static = build_static(CONFIG.site.public)

    # Add components to phml compiler
    phml.add(components.full_paths(), strip=CONFIG.site.components) # type: ignore

    if display_files:
        Logger.custom(f"({len(root)}) files found", label="File System", clr="178")
        Logger.message(root).flush()

    # Render all the pages
    Logger.debug(f"Rendering pages to {TED.parse(f'[@F yellow $]{CONFIG.site.dest}')}").flush()
    render_pages(root, static, nav=nav, out=CONFIG.site.dest, phml=phml)
    write_static_files(root, static, out=CONFIG.site.dest)

    Logger.info("Finished building pages").flush()
    return root, components, phml
