from __future__ import annotations
from functools import cached_property
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from typing import Any, Optional
from .util import normpath, create_uri, splitall
from os import path
from os import getcwd


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
        prefix = normpath(parent_).split("/")[0]
        self.prefix = prefix if prefix != '.' else ""
        self.parent = normpath('/'.join(normpath(parent_).split("/")[1:]))
        self.name = name_.replace(ext_, '')
        self.file_name = name_
        self.ext = ext_
        self.next = None
        self.previous = None
        self.is_blank = is_blank_
        self.meta = {}
        self.content = ""

        if path.isfile(self.full_path):
            with open(self.full_path, "r", encoding="utf-8") as file_content:
                environment = Environment(loader=FileSystemLoader("./"))
                if self.ext == ".md":
                    import frontmatter

                    self.meta, self.content = frontmatter.parse(file_content.read())
                    try:
                        self.template = environment.get_template(self.full_path)
                    except:
                        self.template = None
                else:
                    self.content = file_content.read()
                    self.template = environment.get_template(self.full_path)
        else:
            self.meta, self.content, self.template = {}, "", None

    @cached_property
    def full_path(self) -> str:
        """Returns the relative path with filename and extension."""
        return normpath(path.join(self.prefix, self.parent, self.file_name))

    @cached_property
    def uri(self) -> str:
        """The uri that is associated with this page."""
        if self.name.lower() in ["index", "readme"]:
            return f'{self.parent}'
        else:
            return f'{create_uri(self.parent, self.name)}'

    @classmethod
    def build_uri(cls, path: Path) -> str:
        """The uri that is associated with this page."""
        name = path.name.replace(path.suffix, "")
        parent = normpath('/'.join(normpath(path.parent.as_posix()).split("/")[1:]))
        if name.lower() in ["index", "readme"]:
            return f'{parent}'
        else:
            return f'{create_uri(parent, name)}'

    @cached_property
    def breadcrumb(self) -> list[str]:
        """The individual parts of the path for the uri.

        Returns:
            list[str]: List of directories leading to the final uri
        """
        return splitall(self.uri)

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
