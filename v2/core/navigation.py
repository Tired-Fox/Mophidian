from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from .config.config import Config
from .files import Files, File
from .pages import Page

if TYPE_CHECKING:
    from .pages import Page


class Nav:
    def __init__(self, items: list[Union[Page, Group]], pages: list[Page]):
        self.items = items  # Nested list with compiled Group's, and Page's.
        self.pages = pages  # Flattened list of Page's in order.

        self.homepage = None
        for page in pages:
            if page.is_homepage:
                self.homepage = page
                break

    def __repr__(self):
        return "\n".join(item.pretty() for item in self)

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)


class Group:
    title: str
    """The title of the section."""

    parent: Optional[Group]
    """The immediate parent of the section or `None` if the section is at the top level."""

    children: Optional[list[Union[Page, Group]]]
    """An iterable of all child navigation objects. Children may include nested sections, pages and links."""

    is_group: bool = False
    """Indicates that the navigation object is a "group" object."""

    is_page: bool = False
    """Indicates that the navigation object is a "page" object."""

    def __init__(self, title: str, children: list[Union[Page, Group]]) -> None:
        self.parent = None
        self.children = children
        self.title = title
        self.is_group = True

    def __repr__(self):
        return f"Section(title='{self.title}')"

    @property
    def breadcrumbs(self):
        if self.parent is None:
            return []
        return [self.parent] + self.parent.breadcrumbs

    def pretty(self, depth: int = 0) -> str:
        """Generate an indented form of this object."""
        output = [f"{'  '*depth}{repr(self)}"]
        if self.children is not None:
            for item in self.children:
                output.append(item.pretty(depth + 2))

        return "\n".join(output)


def get_navigation(pages: Files, content: Files, config: Config) -> Nav:
    """Build navigation from files."""
    # TODO Read in additional links from config
    tokens = _get_tokens(pages, content, config)

    nav = []
    webpages = []
    for token in tokens:
        if isinstance(tokens[token], dict):
            children, wp = _get_children(tokens[token])
            nav.append(Group(token, children))
            webpages.extend(wp)
        elif isinstance(tokens[token], File):
            nav.append(Page(tokens[token]))

    _build_np_links(webpages)  # build next and previous links
    _build_parent_links(nav)  # build parent links
    navigation = Nav(nav, webpages)

    print(navigation)
    return navigation


def _build_parent_links(nav) -> None:
    """Add the parent links to all items in nav object."""
    for item in nav:
        if item.is_group:
            for child in item.children:
                child.parent = item
            _build_parent_links(item.children)


def _build_np_links(nav: list[Page]):
    """Build the next and previous links for all pages.

    Args:
        nav (list[Page]): The list of all [Page][mophidian.core.pages.Page] objects.
    """
    pages = [None, *nav, None]
    zipped = zip(pages[:-2], nav, pages[2:])
    for prev, cur, next in zipped:
        cur.previous, cur.next = prev, next


def _get_children(tokens: dict) -> tuple[list[Page | Group], list[Page]]:
    nav = []
    pages = []
    for token in tokens:
        if isinstance(tokens[token], dict):
            children, p = _get_children(tokens[token])
            nav.append(Group(token, children))
            pages.extend(p)
        elif isinstance(tokens[token], File):
            page = Page(tokens[token])
            nav.append(page)
            pages.append(page)

    return nav, pages


def _get_tokens(pages: Files, content: Files, config: Config) -> dict:
    tokenized = {}

    if config.nav.directory_url:
        tokenized = _build_directory_url(tokenized, pages, content)
    else:
        tokenized = _build_non_directory_url(tokenized, pages, content)

    return tokenized


def _build_non_directory_url(tokenized: dict, pages: Files, content: Files) -> dict:
    for file in pages:
        if file.is_dyn:
            for cnt in content.dir_pages(file.parent):
                if cnt.is_type(".md"):
                    tokenized = _add_non_directory_page(tokenized, cnt)
        elif file.is_rdyn:
            for cnt in content.rdir_pages(file.parent):
                if cnt.is_type(".md"):
                    tokenized = _add_non_directory_page(tokenized, cnt)
        else:
            if not file.is_static:
                tokenized = _add_non_directory_page(tokenized, file)

    return tokenized


def _build_directory_url(tokenized: dict, pages: Files, content: Files) -> dict:
    for file in pages:
        if file.is_dyn:
            for cnt in content.dir_pages(file.parent):
                if cnt.is_type(".md"):
                    tokenized = _add_directory_page(tokenized, cnt)
        elif file.is_rdyn:
            for cnt in content.rdir_pages(file.parent):
                if cnt.is_type(".md"):
                    tokenized = _add_directory_page(tokenized, cnt)
        else:
            if not file.is_static:
                tokenized = _add_directory_page(tokenized, file)

    return tokenized


def _add_directory_page(tokenized: dict, file: File):
    breadcrumbs = [crumb for crumb in file.url.split("/") if crumb]
    current = tokenized
    for crumb in breadcrumbs:
        if crumb not in current:
            current.update({crumb: {}})
        current = current[crumb]
    current["index"] = file

    return tokenized


def _add_non_directory_page(tokenized: dict, file: File):
    breadcrumbs = [crumb for crumb in file.url.split("/") if crumb]
    current = tokenized
    for crumb in breadcrumbs[:-1]:
        if crumb not in current:
            current.update({crumb: {}})
        current = current[crumb]
    current[breadcrumbs[-1]] = file

    return tokenized
