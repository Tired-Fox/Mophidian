
from teddecor import TED, Logger
from phml import PHML

from mophidian import CONFIG, states
from .context import Mophidian, MOPHIDIAN_TYPES
from .construct import *
from .render import *

__all__ = [
    "build",
    "render_pages",
    "write_static_files",
    "generate_sitemaps",
    "generate_rss",
]

def build(dirty: bool = False, live_reload: bool = False):
    """Take the components and files and render and write them to the given output directory."""

    Logger.debug("Building pages")

    #? Init phml parser/compiler with globally exposed variables
    phml = PHML()
    phml.expose(mophidian=Mophidian(), **MOPHIDIAN_TYPES)

    Logger.debug("Discovering files and components")

    #? Discover all files and build nav
    components = construct_components(CONFIG.site.components)
    file_system, nav = construct_file_system(CONFIG.site.source)
    public = construct_static(CONFIG.site.public)

    for page in nav.section('blog').pages:
        input(page.title)

    #? Add components to phml compiler
    phml.add(
        *[(cmpt.cname, cmpt.full_path) for cmpt in components.components()],
        strip=CONFIG.site.components
    ) # type: ignore

    #? Render all the pages
    dest = states["dest"]
    Logger.debug(f"Rendering pages to {TED.parse(f'[@F yellow $]{dest}')}")

    render_pages(
        file_system,
        public,
        components,
        nav=nav,
        out=dest,
        phml=phml,
        live_reload=live_reload,
        dirty=dirty
    )
    write_static_files(file_system, public, out=dest, dirty=dirty)

    Logger.debug("Finished building pages")
    return file_system, public, components, phml