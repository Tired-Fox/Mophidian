from dataclasses import dataclass
from .config import CONFIG

from .FileSystem.nodes import (
    Page,
    Markdown,
    Nav,
    Static,
    Layout,
    Directory,
    Group,
    Renderable,
    File,
    Container,
    TOC,
    Anchor
)

MOPHIDIAN_TYPES = {
    "Page": Page,
    "Markdown": Markdown,
    "Nav": Nav,
    "Static": Static,
    "Layout": Layout,
    "Directory": Directory,
    "Group": Group,
    "Renderable": Renderable,
    "File": File,
    "Container": Container,
    "TOC": TOC,
    "Anchor": Anchor,
}

@dataclass
class Mophidian:
    """Class to hold globals to expose to the phml compiler."""

    # Config values
    site_name = CONFIG.site.name
    favicon = CONFIG.build.favicon
    version = CONFIG.site.version
    code_hl_stylesheet = CONFIG.markdown.pygmentize.path   
