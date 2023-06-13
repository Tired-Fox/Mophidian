import os
from saimll import SAIML, Logger
from phml import HypertextManager

from mophidian.old import CONFIG, STATE, init_phml
from mophidian.old.compile_steps import init_steps
from mophidian.old.core.util import filter_sort
from .context import Mophidian
from .construct import *
from .render import *

__all__ = [
    "build",
    "render_pages",
    "write_static_files",
]

init_steps()

def build(dirty: bool = False, scripts: bool = False):
    """Take the components and files and render and write them to the given output directory."""

    phml = init_phml()

    if scripts:
        Logger.Debug("Running pre build commands")
        for command in CONFIG.build.scripts.pre:
            Logger.Debug(command)
            os.system(command)

    Logger.Debug("Building pages")

    # ? Init phml parser/compiler with globally exposed variables

    Logger.Debug("Discovering files and components")

    # ? Discover all files and build nav
    components = construct_components(CONFIG.site.components)
    file_system, nav = construct_file_system(CONFIG.site.source)
    public = construct_static(CONFIG.site.public)

    # ? Add components to phml compiler
    for cmpt in components.components():
        phml.add(cmpt.full_path, ignore=CONFIG.site.components)

    # ? Render all the pages
    dest = STATE.dest
    Logger.Debug(f"Rendering pages to {SAIML.parse(f'[@F yellow $]{dest}')}")
    Logger.Debug(f"\n{file_system}")

    render_pages(file_system, public, components, nav=nav, out=dest, phml=phml, dirty=dirty)
    write_static_files(file_system, public, out=dest, dirty=dirty)

    Logger.Debug("Finished building pages")

    if scripts:
        Logger.Debug("Running post build commands")
        for command in CONFIG.build.scripts.post:
            Logger.Debug(command)
            os.system(command)

    return file_system, public, components, phml

