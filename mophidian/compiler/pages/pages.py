from __future__ import annotations


from copy import copy
from json import JSONEncoder
from typing import Any, Iterable

from .page import Page
from .util import splitall


class CustomEncoder(JSONEncoder):
    def default(self, z):
        if isinstance(z, Page):
            return dict(z)
        else:
            return super().default(z)


class Pages:
    pages: dict[str, Page | dict]
    """List of all the pages."""

    def __init__(self):
        self.pages: dict[str, Page | dict] = {}
        self.length = 0

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
                    else:
                        self.length += 1
                else:
                    self.length += 1

            except IndexError as e:
                self.length += 1

            self[page_.uri] = page_

        # TODO Add previous and next linking

    def flat(self) -> Iterable[Page]:
        """Return an iterable of all the pages.

        Returns:
            Iterable[Page]: Iterate linearly through the dictionary of routes

        Yields:
            Page: A page in the route
        """
        output = []

        def get_values(section_: dict) -> Iterable[Page]:
            for key in section_:
                if isinstance(section_[key], dict):
                    yield from get_values(section_[key])
                elif isinstance(section_[key], Page) and not section_[key].is_blank:
                    yield section_[key]

        if "." in self.pages:
            yield self.pages["."]["index"]
        for key in self.pages:
            if key != ".":
                yield from get_values(self.pages[key])

    def tolist(self) -> list[Page]:
        """Convert the collection to a static list of all the pages.

        Returns:
            list[Page]: List of all the currently stored pages.
        """
        output = []

        def get_values(section_: Any) -> list[Page]:
            output: list[Page] = []
            for key in section_:
                if isinstance(section_[key], dict):
                    output.extend(get_values(section_[key]))
                elif isinstance(section_[key], Page) and not section_[key].is_blank:
                    output.append(section_[key])
            return output

        if "." in self.pages:
            output.append(self.pages["."]["index"])
        for key in self.pages:
            if key != ".":
                output.extend(get_values(self.pages[key]))

        return output

    def index(self, uri: str) -> int:
        """Get the index of a page with a certain uri.

        Args:
            uri (str): The uri of the page to index

        Returns:
            int | None: The index of the found page. None if the page is not found.
        """
        uris = [page.uri for page in self.tolist()]
        return uris.index(uri)

    def __iter__(self):
        self.n = iter(self.flat())
        return self

    def __next__(self):
        return next(self.n)

    def __getitem__(self, idx: Any) -> Any:
        # Get a page based on it's uri
        if isinstance(idx, str):
            for page in self.tolist():
                if page.uri == idx:
                    return page

            bold = "\x1b[1m"
            style = "\x1b[31m"
            rc = "\x1b[37m"
            reset = "\x1b[0m"
            raise IndexError(f"{bold}URI ['{style + idx + rc}'] is not a valid uri{reset}")
        elif isinstance(idx, int):
            return self.tolist()[idx]
        elif isinstance(idx, slice):
            return self.tolist()[idx.start : idx.stop : idx.step]

        return Page.blank()

    def __setitem__(self, dir: str, newvalue: Page):
        # convert an index or slice or tuple/list of indexed and return all that are matching
        current: dict[str, Page | dict] = self.pages
        for token in splitall(dir):
            if token not in current:
                current[token] = {"index": Page.blank()}
            current: dict[str, Page | dict] = current[token]

        current["index"] = newvalue
        index = self.index(newvalue.uri)
        if index >= 1:
            try:
                previous = self[index - 1]
                self[newvalue.uri].previous = previous.uri
                self[previous.uri].next = newvalue.uri
            except Exception as e:
                self[newvalue.uri].previous = None

        try:
            next = self[index + 1]
            self[newvalue.uri].next = next.uri
            self[next.uri].previous = newvalue.uri
        except Exception as e:
            self[newvalue.uri].next = None

    def __delitem__(self, uri: str):
        current = self.pages
        nav = splitall(uri)[:-1]
        last = splitall(uri)[-1]
        for token in nav:
            if token in current.keys():
                current = current[token]
            else:
                IndexError(f"Not a valid uir {{ {uri} }}")

        if last not in current.keys():
            bold = "\x1b[1m"
            style = "\x1b[31m"
            rc = "\x1b[37m"
            reset = "\x1b[0m"
            raise IndexError(f"{bold}Invalid URI [{'/'.join(nav) + style + last + rc}]{reset}")

        # Store the previous and next
        tp = copy(current[last]["index"].previous)
        tn = copy(current[last]["index"].next)

        # Update previous and next for linked pages
        self[tp].next = tn
        self[tn].previous = tp

        if len(current[last].keys()) > 1:
            # "delete" the page at the index location
            current[last]["index"] = Page.blank()
        else:
            del current[last]

    def __len__(self) -> int:
        return self.length

    def print_sub(self, path: str, current: dict, indent: int = 2) -> str:
        index = current["index"]
        output = [
            f"{f'> {path}'}",
            f"{' ' * (indent)}{f'+ {index.uri}' if index is not None else f'- index.html (empty)' }",
        ]

        for entry in current:
            if entry == "index":
                continue
            else:
                output.append(self.print_sub(f"{path}/{entry}", current[entry], indent=indent + 2))

        return '\n'.join(output)

    def __str__(self) -> str:
        from json import dumps

        return dumps(self.pages, indent=2, cls=CustomEncoder)
        # return self.print_sub("", self.pages)
