from saimll import SAIML, Logger
from phml import PHML

from mophidian import CONFIG, states
from .context import Mophidian
from .construct import *
from .render import *

__all__ = [
    "build",
    "render_pages",
    "write_static_files",
    "generate_sitemaps",
    "generate_rss",
]


def build(dirty: bool = False):
    """Take the components and files and render and write them to the given output directory."""

    Logger.Debug("Building pages")

    # ? Init phml parser/compiler with globally exposed variables
    phml = PHML()
    phml.expose(mophidian=Mophidian())

    Logger.Debug("Discovering files and components")

    # ? Discover all files and build nav
    components = construct_components(CONFIG.site.components)
    file_system, nav = construct_file_system(CONFIG.site.source)
    public = construct_static(CONFIG.site.public)

    # ? Add components to phml compiler
    phml.add(
        *[(cmpt.cname, cmpt.full_path) for cmpt in components.components()],
        strip=CONFIG.site.components,
    )  # type: ignore

    # ? Render all the pages
    dest = states["dest"]
    Logger.Debug(f"Rendering pages to {SAIML.parse(f'[@F yellow $]{dest}')}")
    Logger.Debug(f"\n{file_system}")

    render_pages(file_system, public, components, nav=nav, out=dest, phml=phml, dirty=dirty)
    write_static_files(file_system, public, out=dest, dirty=dirty)

    Logger.Debug("Finished building pages")
    return file_system, public, components, phml
