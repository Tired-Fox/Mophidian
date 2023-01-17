from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .files import Renderable

__all__ = [
    "Nav"
]

class Nav:
    def __init__(self, name: str) -> None:
        self.children = []
        self.name = name

    def add(self, item):
        """Add a page or sub nav to the current nav object."""
        self.children.append(item)

    def get(self, url: str) -> Renderable | Nav | None:
        segments = [segment for segment in url.strip("/").split("/") if segment != ""]

        def recurse_get(segments: list[str], context: Nav, url: str) -> Renderable | Nav | None:

            pages = context.pages()
            navs = context.navs()
            new_seg = segments[0] if len(segments) > 0 else ""
            for page in pages:
                if Path(url).joinpath(new_seg).as_posix() + "/" == page.relative_url:
                    return page

            if len(segments) == 0:
                return context

            for nav in navs:
                if nav.name == segments[0]:
                    return recurse_get(segments[1:], nav, url + f"{segments[0]}/")

            return None

        if len(segments) == 0:
            for page in self.pages():
                if page.relative_url == "/":
                    return page
            return self
        else:
            return recurse_get(segments, self, "/")

    def remove(self, item: Renderable | Nav):
        """Remove a page or sub nav from the curren nav object."""
        index = -1
        if isinstance(item, Renderable):
            # TODO: recursive check url with sub navs
            for i, child in enumerate(self.children):
                if isinstance(child, Renderable) and item.relative_url == child.relative_url:
                    index = i
                    break
            error_message = f"Invalid page url {item.relative_url!r}"
        elif isinstance(item, Nav):
            for i, child in enumerate(self.children):
                if isinstance(child, Nav) and item.name == child.name:
                    index = i
                    break
            error_message = f"Invalid nav name {item.name!r}"

        if index == -1:
            raise IndexError(error_message)

        self.children.pop(index)

    def print(self, depth: int = 0) -> str:
        """Colored terminal representation of the file."""
        out = f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m \
(\x1b[34m{self.name}\x1b[0m)"
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out

    def __str__(self) -> str:
        return self.print()

    def __repr__(self) -> str:
        return f"Nav({self.name!r}, children={len(self.children)})"

    def pages(self) -> list[Renderable]:
        """List of all renderable pages in the nav."""
        return [page for page in self.children if isinstance(page, Renderable)]

    def navs(self) -> list[Nav]:
        """List of all sub navs in the nav."""
        return [nav for nav in self.children if isinstance(nav, Nav)]

    def __iter__(self):
        """Iterate over the pages and sub navs in order. Starts with pages in alphabetical order
        based on their url's. Next it will iterate over the sub navs in alphabetical order based on
        sub nav name.
        """
        pages = self.pages()
        navs = self.navs()

        pages.sort(key=lambda p: p.url)
        navs.sort(key=lambda n: n.name)

        for page in pages:
            yield page

        for nav in navs:
            yield nav