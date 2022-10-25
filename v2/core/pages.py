from __future__ import annotations
from inspect import getmembers
from optparse import Option


from typing import TYPE_CHECKING, Any, MutableMapping, Optional, Union
from urllib.parse import urljoin
from .files import File

if TYPE_CHECKING:
    from .navigation import Group


class Page:
    """Page"""

    title: Optional[str]
    """Title of the page."""

    markdown: Optional[str]
    """The original markdown from the file."""

    content: Optional[str]
    """The rendered Markdown or Template from the file. This is what is written to file."""

    toc: Any  # TODO Create cusom classes for TOC. Type annotate the pydoc
    """Iterable representation of the toc of a page."""

    meta: MutableMapping[str, Any]
    """Metadata of a markdown page. Built from yaml frontmatter."""

    file: File
    """The file the page is being rendered from. [File][mophidian.core.files.File]."""

    full_url: Optional[str]
    """The full url including the base path and the website url."""

    previous: Optional[Page]
    """The [page][mophidian.core.pages.Page] object for the previous page or `None`."""

    next: Optional[Page]
    """The [page][mophidian.core.pages.Page] object for the next page or `None`."""

    parent: Optional[Group]
    """The immediate parent of the section or `None` if the section is at the top level."""

    children: None = None
    """An iterable of all child navigation objects. Since pages don't contain children then children is always None."""

    is_group: bool = False
    """Indicates that the navigation object is a "group" object."""

    is_page: bool = False
    """Indicates that the navigation object is a "page" object."""

    def pretty(self, depth: int = 0) -> str:
        """Generate an indented form of this object."""
        title = self.title if self.title is not None else "(BLANK)"
        return f"{'  '*depth}Page(title: {title}, url: {self.url})"

    @property
    def breadcrumbs(self):
        if self.parent is None:
            return []
        return [self.parent].extend(self.parent.breadcrumbs)

    @property
    def is_index(self) -> bool:
        return self.file.name == "index"

    @property
    def is_root_level(self) -> bool:
        return self.parent is None

    @property
    def is_homepage(self) -> bool:
        return self.is_root_level and self.is_index and self.file.url in [".", "index.html"]

    def __init__(self, file: File, title: Optional[str] = None):
        file.page = self
        self.file = file
        self.title = title

        #  Nav
        self.parent = None
        self.children = None
        self.previous = None
        self.next = None

        self._build_urls("https://tired-fox.github.io/mophidian/")
        self.is_page = True

    def __eq__(self, other: Page) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.file == other.file
            and self.title == other.title
        )

    def __repr__(self) -> str:
        title = self.title if self.title is not None else '(BLANK)'
        url = self.file.url
        return f"Page(title={title}, url='{url}')"

    @property
    def url(self) -> str:
        return '' if self.file.url == '.' else self.file.url

    def _build_urls(self, domain: str):
        if domain:
            if not domain.endswith("/"):
                domain += "/"
            self.full_url = urljoin(domain, self.url)
        else:
            self.full_url = None
