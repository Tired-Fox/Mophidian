from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, Union

from mophidian.core.files import Files, File, FileExtension
from mophidian.core.pages import Page


if TYPE_CHECKING:
    from .config.config import Config


class Nav:
    def __init__(self, items: list[Union[Page, Group]], pages: list[Page]):
        self.items = items  # Nested list with compiled Group's, and Page's.
        self.pages = pages  # Flattened list of Page's in order.

        self.homepage = None
        for page in pages:
            if page.is_homepage:
                self.homepage = page
                break

    def get_dir(self, dir: str):
        """Get the item at the given directory. This gives the user the ability to jump to a directory and begin looping there.

        Args:
            dir (str): The directory/group item.
        """
        tokens = [
            token
            for token in os.path.normpath(dir).replace("\\", "/").split("/")
            if token not in ["", ".", None]
        ]

        def recurse(item: Group, tokens: list) -> Group | None:
            if len(tokens) == 0:
                return item
            else:
                for i in item.children:
                    if isinstance(i, Group):
                        if i.title == tokens[0]:
                            return recurse(item, tokens[1:])
                return None

        if len(tokens) > 0:
            for item in self.items:
                if isinstance(item, Group):
                    if item.title == tokens[0]:
                        return recurse(item, tokens[1:])
        return None

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

    children: list[Union[Page, Group]]
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
        self.index = None

    def __repr__(self):
        return f"Section(title='{self.title}')"

    def has_index(self) -> bool:
        for child in self.children:
            if isinstance(child, Page) and child.file.is_index:
                self.index = child
                return True
        return False

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
    for token in tokens:
        if isinstance(tokens[token], dict):
            children = _get_children(tokens[token], config)
            nav.append(Group(token, children))
        elif isinstance(tokens[token], File):
            new_page = Page(tokens[token], config)
            nav.append(new_page)

    _sort_links(nav)
    webpages = _extract_links(nav)

    _build_np_links(webpages)  # build next and previous links
    _build_parent_links(nav)  # build parent links
    navigation = Nav(nav, webpages)

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


def _get_children(tokens: dict, config: Config) -> list[Page | Group]:
    nav = []
    for token in tokens:
        if isinstance(tokens[token], dict):
            children = _get_children(tokens[token], config)
            nav.append(Group(token, children))
        elif isinstance(tokens[token], tuple):
            page = Page(tokens[token][0], config)
            page.build_template(tokens[token][1])
            nav.append(page)
        elif isinstance(tokens[token], File):
            page = Page(tokens[token], config)
            nav.append(page)

    return nav


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
            if not file.is_static and not file.is_type(FileExtension.SASS):
                tokenized = _add_non_directory_page(tokenized, file)

    return tokenized


def _build_directory_url(tokenized: dict, pages: Files, content: Files) -> dict:
    for file in pages:
        if file.is_dyn:
            for cnt in content.dir_pages(file.parent):
                if cnt.is_type(".md"):
                    tokenized = _add_directory_page(tokenized, cnt, file)
        elif file.is_rdyn:
            for cnt in content.rdir_pages(file.parent):
                if cnt.is_type(".md"):
                    tokenized = _add_directory_page(tokenized, cnt, file)
        else:
            if not file.is_static and not file.is_type(FileExtension.SASS):
                tokenized = _add_directory_page(tokenized, file)

    return tokenized


def _add_directory_page(tokenized: dict, file: File, template=None):
    breadcrumbs = [crumb for crumb in file.url.split("/") if crumb not in ["", ".", None]]
    current = tokenized
    for crumb in breadcrumbs:
        if crumb not in current:
            current.update({crumb: {}})
        current = current[crumb]
    current["index"] = file if template is None else (file, template)

    return tokenized


def _add_non_directory_page(tokenized: dict, file: File, template=None):
    breadcrumbs = [crumb for crumb in file.url.split("/") if crumb]
    current = tokenized
    for crumb in breadcrumbs[:-1]:
        if crumb not in current:
            current.update({crumb: {}})
        current = current[crumb]
    current[breadcrumbs[-1]] = file if template is None else (file, template)

    return tokenized


def _extract_links(links: list):
    def get_links(items: list) -> list:
        result = []

        for item in items:
            if isinstance(item, Page):
                result.append(item)
            else:
                result.extend(get_links(item.children))

        return result

    return get_links(links)


def _sort_links(links: list):
    def sort_group(children: list) -> list:
        result = []
        groups = list(filter(lambda item: item.is_group, children))

        def sort_func(e):
            # "!" tagged items are put to the front in sorting and "~" tagged items are put to the end.
            # It is a easy way of using builtin sorting but also giving priorities.
            if isinstance(e, Page) and e.file.dest_name == "index":
                # Add ! to front as it will give it priority to be first
                return f"!{e.file.dest_name}"
            else:
                # Add ~ to front as it will give it priority to be last
                return f"~{e.title.lower()}"

        children.sort(key=sort_func)
        result.extend(children)

        for item in groups:
            item.children = sort_group(item.children)

        return result

    links = sort_group(links)
