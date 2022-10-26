from __future__ import annotations


from typing import TYPE_CHECKING, Any, MutableMapping, Optional
from urllib.parse import urljoin

from .config.config import Config
from .files import File, FileExtension
from moph_log import Logger
from .utils import MophidianMarkdown, renderTemplate

if TYPE_CHECKING:
    from .navigation import Group
    from jinja2 import Template
    from .navigation import Nav


class Page:
    """Page"""

    title: Optional[str]
    """Title of the page."""

    markdown: Optional[str]
    """The original markdown from the file."""

    template: Optional[Template]
    """The Jinja2 template associated with this page."""

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
        title = self.title if self.title is not None else '(BLANK)'
        url = self.file.url
        next = self.next.url if self.next is not None else "(BLANK)"
        prev = self.previous.url if self.previous is not None else "(BLANK)"
        parent = self.parent.title if self.parent is not None else "(BLANK)"
        return f"{'  '*depth}Page(title={title}, url='{url}', next: {next}, prev: {prev}, parent: {parent})"

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

        # For build process
        self.template = None
        self.toc = None
        self.content = None
        self.markdown = None
        self.meta = {}

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
        next = self.next.url if self.next is not None else "(BLANK)"
        prev = self.previous.url if self.previous is not None else "(BLANK)"
        parent = self.parent.is_group if self.parent is not None else "(BLANK)"
        return f"Page(title={title}, url='{url}', next: {next}, prev: {prev}, parent: {parent})"

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

    def build_content(self, config: Config, layouts: dict[str, dict | Template]):
        """Build the pages content. Parse the meta data from a markdown file everything else is the content."""
        try:
            # Use utf-8-sig to more reliably ensure utf-8 encoding. utf-8 with BOM
            with open(self.file.abs_src_path, encoding="utf-8-sig", errors="strict") as source:
                content = source.read()
        except OSError:
            Logger.Error(f"File not found: {self.file.abs_src_path}")
            raise
        except ValueError:
            Logger.Error(f"Encoding error for file: {self.file.abs_src_path}")
            raise

        if self.file.is_type(FileExtension.Markdown):
            self.meta, self.markdown, self.template = MophidianMarkdown.parse(
                content, config, layouts
            )
        elif self.file.is_type(FileExtension.Template) and self.template is None:
            self.content = content

        self._build_title()

    def render(
        self,
        config: Config,
        components: dict[str, dict | Template],
        layouts: dict[str, dict | Template],
        nav: Nav,
    ):
        """Compiles the page into html.

        Args:
            config (Config): Mophidian config
            components (dict[str, dict | Template]): Dictionary of jinja2.Template components
            layouts (dict[str, dict | Template]): Dictionary of jinja2.Template layouts
            nav (Nav): Navigation object
        """
        if self.file.is_type(FileExtension.Markdown):
            self.content, self.toc = MophidianMarkdown.render(
                self, nav, config, components, layouts
            )
        else:
            self.content = renderTemplate(self, nav, config, components, layouts)

    def _build_title(self):
        """Build the title based on the parsed content."""

        title = None
        if self.file.is_type(FileExtension.Markdown):
            if 'title' in self.meta:
                self.title = self.meta["title"]
                return

            title = MophidianMarkdown.get_title(self.markdown if self.markdown is not None else "")

        if title is None:
            if self.is_homepage:
                title = "Home"
            else:
                title = self.file.name.replace('-', ' ').replace('_', ' ')
                if title.lower() == title:
                    title = title.capitalize()

        self.title = title
