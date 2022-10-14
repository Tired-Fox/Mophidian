from __future__ import annotations
from copy import copy, deepcopy
from email.generator import Generator
from json import JSONEncoder

from os import path
from textwrap import indent
from typing import Any, Iterable, TypeVar, Union, Optional


def normpath(path_: str) -> str:
    """Normalize the path and make it alwasy have forward slash."""
    return path.normpath(path_).replace("\\", "/")


def create_uri(parent_: str, name_: str) -> str:
    """Takes the parent path and the name of the file and returns the uri.

    Args:
        parent_ (str): The parent path of the file
        name_ (str): The file name

    Returns:
        str: The normalized combination of the parent and the name
    """
    return normpath(path.join(parent_, name_))


def splitall(path: str) -> list[str]:
    path = normpath(path)
    return path.split('/')


class Pages:
    pages: dict[str, Page | dict]
    """List of all the pages."""

    def __init__(self):
        self.pages: dict[str, Page | dict] = {}

    def append(self, page_: Page):
        """Append the page to the collection of pages. It will group it based on the parent directory.

        Args:
            page_ (Page): The page to add to the collection.
        """
        if "[slug]" not in page_.uri or "[...slug]" not in page_.uri:
            try:
                page = self[page_.uri]

                if page_.name.lower() in ["index", "readme"]:
                    if not page.is_blank:
                        if page.has_priority(page_):
                            return
                    self[page_.uri] = page_
            except IndexError:
                pass

            self[page_.uri] = page_

        # TODO Add previous and next linking

    def flat(self) -> Iterable[Page]:
        """_summary_

        Returns:
            Iterable[Page]: Iterate linearly through the dictionary of routes

        Yields:
            Page: A page in the route
        """
        output = []

        def get_values(section_: dict) -> Iterable[Page]:
            for key in section_:
                if isinstance(section_[key], dict):
                    for page in get_values(section_[key]):
                        yield page
                elif isinstance(section_[key], Page) and not section_[key].is_blank:
                    yield section_[key]

        if "." in self.pages:
            yield self.pages["."]["index"]
        for key in self.pages:
            if key != ".":
                for page in get_values(self.pages[key]):
                    yield page

    def __iter__(self):
        self.n = iter(self.flat())
        return self

    def __next__(self):
        return next(self.n)

    def __getitem__(self, idx: str | slice | int) -> list[Page] | Page:
        # Get a page based on it's uri
        if isinstance(idx, str):
            for page in self:
                if page.uri == idx:
                    return page
        elif isinstance(idx, int):
            for i, page in enumerate(self):
                if i == idx:
                    return page
        elif isinstance(idx, slice):
            return list(self)[idx.start : idx.stop : idx.step]

        return Page.blank()

    def __setitem__(self, dir: str, newvalue: Page):
        # convert an index or slice or tuple/list of indexed and return all that are matching
        current: dict[str, Page | dict] = self.pages
        for token in splitall(dir):
            if token not in current:
                current[token] = {"index": Page.blank()}
            current: dict[str, Page | dict] = current[token]

        current["index"] = newvalue

    def __delitem__(self, uri: str):
        current = self.pages
        nav = splitall(uri)[:-1]
        last = splitall(uri)[-1]
        for token in nav:
            if token in current:
                current = current[token]
            else:
                IndexError(f"Not a valid uir {{ {uri} }}")

        if len(current[last].keys()) > 1:
            current[last]["index"] = Page.blank()
        else:
            del current[last]

    #     def __len__(self) -> int:
    #         return sum([len(self.pages[entry]) for entry in self.pages])

    def print_sub(self, path: str, current: dict, indent: int = 2) -> str:
        index = current["index"]
        output = [
            f"{f'> {path}'}",
            f"{' ' * (indent)}{f'+ {index.uri}' if index is not None else f'- index.html (empty)' }",
        ]

        for entry in current:
            print(f"At path {path} with entry {entry}")
            if entry == "index":
                continue
            else:
                output.append(self.print_sub(f"{path}/{entry}", current[entry], indent=indent + 2))

        return '\n'.join(output)

    def __str__(self) -> str:
        from json import dumps

        return dumps(self.pages, indent=2, cls=CustomEncoder)
        # return self.print_sub("", self.pages)


class CustomEncoder(JSONEncoder):
    def default(self, z):
        if isinstance(z, Page):
            return dict(z)
        else:
            return super().default(z)


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
            return self.parent
        else:
            return create_uri(self.parent, self.name)

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
