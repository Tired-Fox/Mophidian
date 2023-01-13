from pathlib import Path

from phml import PHML
from teddecor import Logger, LL, TED

if True:
    import sys
    sys.path.append("../")
    from config import CONFIG
    from utils import url
    from core import Mophidian

from .nodes import (
    Directory,
    Page,
    Layout,
    REGEX,
    Component,
    Static,
    Markdown,
    Nav,
    File,
    Renderable,
    Group,
    Container
)

from .util import PAGE_IGNORE, title

def build_components(path: str) -> Directory:
    """Find all the components in the given path and construct a file structure."""

    components = Directory(path)
    for file in Path(path).glob("**/*.phml"):
        components.add(Component(file.as_posix()))
    return components

def build_files(path: str) -> tuple[Directory, Nav]:
    """Find all the files in the given path and construct a file structure."""

    root = Directory(path)
    for _file in Path(path).glob("**/*.*"):
        # Pages and Layouts
        if _file.suffix == ".phml":
            if REGEX["layout"]["name"].match(_file.name) is not None:
                root.add(Layout(_file.as_posix()))
            elif REGEX["page"]["name"].match(_file.name) is not None:
                root.add(Page(_file.as_posix()))
            else:
                file_info = REGEX["file"]["name"].search(_file.name)
                file_name, _, _, _ = (
                    file_info.groups() if file_info is not None else ("", None, None, "")
                )
                if file_name in PAGE_IGNORE:
                    root.add(Page(_file.as_posix()))

        # Markdown files
        elif _file.suffix == ".md":
            root.add(Markdown(_file.as_posix()))

        # Static files
        else:
            root.add(Static(_file.as_posix()))

    root.build_hierarchy()
    nav = root.build_nav()
    return root, nav

def render_pages(root: Directory, out: str, phml: PHML, nav: Directory = Directory("")):
    """Render all the pages with their layouts to their destination file."""

    global_vars = {
        "url": url,
        "title_case": title,
        "nav": nav,
        "mophidian": Mophidian()
    }

    # Render pages
    for page in root.renderable():
        page_vars = {
            "title": page.title
        }

        # Ensure path to file
        page.dest(out).parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(page.dest(out), "+w", encoding="utf-8") as file:
            file.write(page.render(phml, **page_vars, **global_vars))

def write_static_files(root: Directory, out: str):
    """Write static files to their destination."""

    for static in root.static():
        static.write(out)

def build(display_files: bool = False):
    """Take the components and files and render and write them to the given output directory."""

    Logger.info("Building pages").flush()
    phml = PHML()

    # Build components and files
    Logger.debug("Discovering files and components").flush()
    components = build_components("components/")
    root, nav = build_files(CONFIG.site.source)

    # Add components to phml compiler
    phml.add(components.full_paths(), strip_root=True) # type: ignore

    if display_files:
        Logger.custom(f"({len(root)}) files found", label="File System", clr="178")
        Logger.message(root).flush()

    # Render all the pages
    Logger.debug(f"Rendering pages to {TED.parse(f'[@F yellow $]{CONFIG.site.dest}')}").flush()
    render_pages(root, nav=nav, out=CONFIG.site.dest, phml=phml)
    write_static_files(root, out=CONFIG.site.dest)

    Logger.info("Finished building pages").flush()
    return root, components, phml
