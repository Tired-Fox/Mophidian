from __future__ import annotations
from ast import dump
from inspect import getmembers
from json import JSONEncoder, dumps
from lib2to3.pgen2 import token

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

    navigation = Nav(nav, webpages)
    print(dumps(tokens, indent=2, cls=ComplexJSONEncoder))
    print(navigation)


def _get_children(tokens: dict) -> tuple[list[Page | Group], list[Page]]:
    nav = []
    pages = []
    for token in tokens:
        if isinstance(tokens[token], dict):
            children, p = _get_children(tokens[token])
            nav.append(Group(token, children))
            pages.extend(pages)
        elif isinstance(tokens[token], File):
            nav.append(Page(tokens[token]))

    return nav, pages


class ComplexJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Files):
            return repr(obj)
        elif isinstance(obj, File):
            return str(obj)
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)


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
