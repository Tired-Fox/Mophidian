from dataclasses import dataclass
from mophidian.config import CONFIG

from mophidian.FileSystem import (
    Page,
    Markdown,
    Nav,
    Static,
    Directory,
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
    "Directory": Directory,
    "Renderable": Renderable,
    "File": File,
    "Container": Container,
    "TOC": TOC,
    "Anchor": Anchor,
}
"""The type objects that will be exposed to the phml pages."""

@dataclass
class Mophidian:
    """Class to hold globals to expose to the phml compiler."""

    site_name = CONFIG.site.name
    favicon = CONFIG.build.favicon
    version = CONFIG.site.version
    code_hl_stylesheet = CONFIG.markdown.pygmentize.path
