__version__ = "0.2.4"

from dataclasses import dataclass
from phml import HypertextManager
from pathlib import Path

from .config import CONFIG

@dataclass
class DestState:
    FINAL = "out"
    """Compile files to `out` folder."""
    DEV = (Path("dist") / CONFIG.site.root).as_posix()
    """Compile files to `dist/{root}` folder."""

class State:
    markdown_code_highlight_warned: bool = False
    dest: str = DestState.DEV

STATE = State()

def init_phml() -> HypertextManager:
    from .core.util import filter_sort
    from .core.build.context import Mophidian
    phml = HypertextManager()
    phml.expose(mophidian=Mophidian(), filter_sort=filter_sort)
    
    for path in Path(CONFIG.site.python).glob("**/*.py"):
        phml.add_module(path.as_posix(), ignore=CONFIG.site.python)

    return phml

phml = init_phml()
