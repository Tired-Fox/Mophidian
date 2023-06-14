from functools import cached_property


class Anchor:
    """Link representation of a header tag."""

    def __init__(self, name: str, link: str, level: int) -> None:
        self._name = name
        self._level = level
        self._id = link.strip().lstrip("#")

    @cached_property
    def link(self) -> str:
        """Link/href of the anchor."""
        return f"#l{self._level}-{self._id}"

    @property
    def name(self) -> str:
        """Name of the anchor."""
        return self._name

    @property
    def level(self) -> int:
        """Anchor/header level."""
        return self._level

    def __eq__(self, __o: object) -> bool:
        return bool(
            isinstance(__o, self.__class__)
            and self.name == __o.name
            and self.link == __o.link
            and self.level == __o.level
        )

    def __repr__(self) -> str:
        return f"{self.name}({self.link!r}, {self.level})"


class TOC:
    """Contains a list of links. Each anchor has a level representing the header level."""

    def __init__(self) -> None:
        self._children = []

    @property
    def links(self) -> list[Anchor]:
        """All the anchor links as a flat list."""
        return self._children

    def __iter__(self):
        for anchor in self._children:
            yield anchor

    def append(self, link: Anchor):
        """Add an anchor object to the toc."""
        self._children.append(link)

    def extend(self, links: list[Anchor]):
        """Extend the anchors in the toc."""
        self._children.extend(links)

    def remove(self, link: Anchor):
        """Remove a specific anchor from the toc."""
        self._children.remove(link)

    def __repr__(self) -> str:
        return f"[{', '.join([repr(child) for child in self._children])}]"
