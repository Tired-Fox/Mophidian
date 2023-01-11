from pathlib import Path

from phml import PHML
from teddecor import Logger

if True:
    import sys
    sys.path.append("../")
    from config import CONFIG
    from utils import url

from .nodes import (
    Directory,
    Page,
    Layout,
    REGEX,
    Component,
    Static,
    Markdown
)

from .util import PAGE_IGNORE

def build_components(path: str) -> Directory:
    """Find all the components in the given path and construct a file structure."""

    components = Directory(path)
    for file in Path(path).glob("**/*.phml"):
        components.add(Component(file.as_posix()))
    return components

def build_files(path: str) -> Directory:
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
    return root

def render_pages(root: Directory, out: str, phml: PHML):
    """Render all the pages with their layouts to their destination file."""

    global_vars = {
        "url": url
    }

    # Render pages
    for page in root.renderable():
        # Ensure path to file
        page.dest(out).parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(page.dest(out), "+w", encoding="utf-8") as file:
            file.write(page.render(phml, **global_vars))

def write_static_files(root: Directory, out: str):
    """Write static files to their destination."""

    for static in root.static():
        static.write(out)

def build():
    """Take the components and files and render and write them to the given output directory."""

    Logger.info("Building pages").flush()
    phml = PHML()

    # Build components and files
    Logger.debug("Discovering files and components").flush()
    components = build_components("components/")
    root = build_files(CONFIG.site.source)

    # Add components to phml compiler
    phml.add(components.full_paths(), strip_root=True) # type: ignore

    # Render all the pages
    Logger.debug("Rendering pages").flush()
    render_pages(root, out=CONFIG.site.dest, phml=phml)
    write_static_files(root, out=CONFIG.site.dest)

    Logger.info("Finished building pages").flush()
    return root, components, phml
