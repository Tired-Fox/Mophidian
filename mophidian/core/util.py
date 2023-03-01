from __future__ import annotations
import re
from functools import cache
from typing import Any, Callable

from markdown import Markdown

from mophidian.config import CONFIG
# from mophidian.file_system.markdown_extensions import _RelativePathExtension


# extensions=[
#     _RelativePathExtension(None, None, None),
#     *
# ],

MARKDOWN = Markdown(
    extensions=CONFIG.markdown.extensions,
    extension_configs=CONFIG.markdown.extension_configs,
)

def filter_sort(
    collection,
    valid: Callable,
    key: str | Callable | None = None
):
    """Filter a iterable collection by the filter and sort it by the sort. The
    filter is a callable similar to the build in filter function. Or it could be
    a type where `isinstance()` is called, or it could be a instance of something
    where a normal comparison is used. The sort is either a str of an attribute
    to get from the collection of or a collable similar to the build in sort
    function.

    First the collection will be filtered and collected into a list then that
    resulting list will be sorted by the given sort or with the default sort
    method.

    Under the hood it is doing something simliar to
    `sorted(list(filter({filter}, {collection})), key={sort})` where
    `filter` = `Callable` and sort` = `getattr(collection, {sort})`
    or `Callable`.

    Args:
        collection: A object that implements `__iter__`, `__getitem__`,
            `__hasitem__`.
        valid (instance | type | Callable): Object isntance to check for equal,
            type to check if it is an instance of, or a Callable to return true
            or false if a value should be kept
        key (str | Callable): The attribute name to get from each collection
            item for sorting or a Callable to return a value for sorting.

    Returns:
        New list that is the filtered and sorted result of the passed in
        collection.
    """
    def filter_value(collection_item: Any) -> bool:
        if isinstance(valid, type):
            return isinstance(collection_item, valid)
        if callable(valid):
            return valid(collection_item)

        return collection_item == valid

    def sort_value(collection_item: Any) -> Any:
        if isinstance(key, str):
            return getattr(collection_item, key)
        elif key is not None:
            return key(collection_item)
        else:
            return collection_item

    return sorted(list(filter(filter_value, collection)), key=sort_value)

def title(text: str | list[str]) -> str:
    """Generate the title case version of the passed in text."""
    tokens = text
    if isinstance(text, str):
        tokens = text.split(" ")
    return " ".join([token[0].upper() + token[1:] for token in tokens])

def url(url: str) -> str:
    """Construct a url given a page url and the project's rool."""

    root = f"/{CONFIG.site.root.strip('/')}/" if CONFIG.site.root != "" else ""
    return root + url.lstrip("/")

@cache
def html(*meta: str) -> str:
    """Construct the base html string based on additional tags and flags."""

    new_line = '\n        '
    meta = [META[tag] for tag in meta if tag in META]

    new_line = "\n"
    addons = f'{new_line + new_line.join(meta) + new_line if len(meta) > 0 else ""}'
    links = "\n" + f'<link rel="shortcut icon" href="{url(CONFIG.build.favicon)}" type="image/x-icon">'

    return f"""\
<!DOCTYPE html>
<html lang="en">

    <head>{addons}{links}
        <title>{{title or ''}}</title>
        <style></style>
    </head>

    <body>
        <Slot />
    </body>

</html>\
"""

META = {
    "charset": '<meta charset="UTF-8">',
    "http_equiv": '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
    "viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
}

PAGE_IGNORE = {
    "404"
}

REGEX = {
    "page": {
        "name": re.compile(r"^(page)(@)?(\w+)?(\.phml)$")
    },    
    "layout": {
        "name": re.compile(r"^(layout)(@)?(\w+)?(\.phml)$")
    },
    "file": {
        "name": re.compile(r"([a-zA-Z_0-9\.]+)(@)?(\w+)?(\.[a-zA-Z]{0,4})")
    },
    "group": {
        "name": re.compile(r"\(([a-zA-Z0-9]+)\)"),
        "path": {
            "start": re.compile(r"\([a-zA-Z0-9]+\)\/"),
            "middle": re.compile(r"\/\([a-zA-Z0-9]+\)\/"),
        }
    }
}