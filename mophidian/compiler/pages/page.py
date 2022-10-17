from __future__ import annotations

from typing import Any, Optional
from .util import normpath, create_uri
from os import path


page_var_type = Optional[str | int | dict[str, Any]]


class Page:
    """The data object for a page. It stores important and relative information for each page."""

    parent: str
    """The parent directory this page is in."""

    name: str
    """File name."""

    ext: str
    """The files extension (md, html, etc.)."""

    content: str
    """The contents of the file before rendering."""

    previous: Optional[str]
    """The previous page."""

    next: Optional[str]
    """The next page."""

    meta: Optional[dict[str, Any]]
    """The parsed frontmatter of a markdown page."""

    def blank() -> Page:
        return Page("", "", "", is_blank_=True)

    def __init__(self, parent_: str, name_: str, ext_: str, is_blank_: bool = False):
        """Initialize the page with the basic file information

        Args:
            parent_ (str): The parent directory for the page
            name_ (str): The name of the file/page
            ext_ (str): The extension for the file
        """
        self.parent = normpath('/'.join(normpath(parent_).split("/")[1:]))
        self.name = name_.replace(ext_, '')
        self.file_name = name_
        self.ext = ext_
        self.next = None
        self.previous = None
        self.is_blank = is_blank_

        if path.isfile(self.full_path):
            with open(self.full_path, "r", encoding="utf-8") as file_content:
                if self.ext == ".md":
                    import frontmatter

                    self.meta, self.content = frontmatter.parse(file_content.read())
                else:
                    self.meta = None
                    self.content = file_content.read()
        else:
            self.meta, self.content = {}, ""

    @property
    def full_path(self) -> str:
        """Returns the relative path with filename and extension."""
        return path.normpath(path.join("pages", self.parent, self.file_name))

    @property
    def uri(self) -> str:
        """The uri that is associated with this page."""
        if self.name.lower() in ["index", "readme"]:
            return f'{self.parent}'
        else:
            return f'{create_uri(self.parent, self.name)}'

    def has_priority(self, page_: Page) -> bool:
        """Return true if current page has priority over the passed in page.

        Args:
            page_ (Page): The page compared against

        Returns:
            bool: True if higher priority
        """
        if self.file_name == "index.html" and page_.file_name != "index.html":
            return True
        elif self.name == "index" and page_.name != "index":
            return True
        elif self.name.lower() == "readme" and page_.name.lower() != "readme":
            return True
        return False

    def asdict(self) -> dict[str, page_var_type]:
        return {self.uri: dict(self)}

    def __iter__(self):
        yield "parent", self.parent
        yield "ext", self.ext
        yield "content", len(self.content)
        yield "name", self.name
        yield "meta", self.meta
        yield "next", self.next
        yield "previous", self.previous

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        from json import dumps

        return dumps(self.asdict(), indent=2)
