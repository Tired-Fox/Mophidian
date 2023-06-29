from .config import MophConfig
from .plugins import Plugin
from .compile import Compiler
from .fs import fsprint

from conterm.logging import Logger

__version__="0.2.5"

logger = Logger(fmt="[{code}] {msg}", codes=[(-1, "DEBUG", "white")])
