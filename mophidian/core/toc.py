from __future__ import annotations
from typing import Any


def build_toc(toc_tokens: list) -> TOC:
    toc = [_parse_token(token) for token in toc_tokens]
    return TOC(toc)


class TOC:
    """Iterable representation of a markdown file table of contents."""

    def __init__(self, links: list):
        self.links = links

    def __iter__(self):
        return iter(self.links)

    def __len__(self) -> int:
        return len(self.links)

    def __str__(self) -> str:
        return '\n'.join(str(link) for link in self.links)


class Anchor:
    """Represents a single link in a table of contents."""

    title: str
    """The label/title of the link."""

    id: str
    """The element id that the link is representing."""

    level: int
    """The depth or nesting level of the link in the TOC."""

    children: list[Anchor]
    """Iterable of nested links."""

    def __init__(self, title: str, id: str, level: int):
        self.title = title
        self.id = id
        self.level = level

        self.children = []

    def url(self) -> str:
        """The href of the link derived from the `id` attribute."""
        return f"#{self.id}"

    def __str__(self):
        return self.pretty()

    def pretty(self, depth=0):
        lspace = "  " * depth
        out = [f"{lspace}{self.title} {{{self.url}}}"]
        for child in self.children:
            out.append(child.pretty(depth + 2))

        return "\n".join(out)


def _parse_token(token: dict[str, Any]):
    anchor = Anchor(token['name'], token['id'], token['level'])
    for i in token['children']:
        anchor.children.append(_parse_token(i))

    return anchor
