__version__ = "1.0.0"

from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG

@dataclass
class DestState:
    PREVIEW = "out"
    """Serve files from out folder."""
    DEV = Path("dist").joinpath(CONFIG.site.root).as_posix()
    """Serve files from dist folder."""

states = {
    "markdown_code_highlight_warned": False,
    "dest": DestState.DEV
}