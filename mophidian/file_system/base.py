from pathlib import Path
from re import sub
from phml import query, AST

from mophidian.config import CONFIG
from mophidian.core.util import REGEX

__all__ = [
    "Node"
]

def build_attributes(attributes: dict) -> dict:
    """Build the props from the dynamic configuration options."""

    props = {}
    for attribute in attributes:
        if isinstance(attributes[attribute], list):
            props[attribute] = " ".join(attributes[attribute])
        elif isinstance(attributes[attribute], (str, int, float)):
            props[attribute] = str(attributes[attribute])
        elif isinstance(attributes[attribute], bool):
            props[attribute] = "yes" if attributes[attribute] else "no"
    return props

def apply_attribute_configs(ast: AST) -> AST:
    """Apply attributes defined in the config to html and body tags."""
    html = query(ast, "html")
    body = query(ast, "body")

    if html is not None:
        html.properties.update(build_attributes(CONFIG.build.html))

    if body is not None:
        body.properties.update(build_attributes(CONFIG.build.body))

    return ast

class Node:
    """Base file system node."""

    root: str
    """Root directory of the path."""

    path: str
    """Full path after the root directory."""

    def __init__(self, path: str, ignore: str = "") -> None:
        path = path.replace("\\", "/").strip("/")
        self.root, self.path = ignore, sub(ignore, "", path)

        self.src = self.path
        while True:
            # Remove group directories from path
            if REGEX["group"]["path"]["middle"].match(self.src) is not None:
                self.src = REGEX["group"]["path"]["middle"].sub("/", self.src)
            elif REGEX["group"]["path"]["start"].match(self.src) is not None:
                self.src = REGEX["group"]["path"]["start"].sub("", self.src)
            else:
                break
        self.full_path = path
        self.children = None

    @property
    def parents(self) -> list[str]:
        """Parent directories as a list of strings."""
        return [node for node in Path(self.path).parent.as_posix().split("/") if node != "."]

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self.__class__) and __o.path == self.path

    def __str__(self) -> str:
        out = f"\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.path!r}\x1b[0m"
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(4)
        return out