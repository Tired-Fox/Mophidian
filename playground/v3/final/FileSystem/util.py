import re
from typing import Any, Callable
from functools import cache

from config import CONFIG
from utils import url

META = {
    "charset": '<meta charset="UTF-8">',
    "http_equiv": '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
    "viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
}

PAGE_IGNORE = {
    "404"
}

@cache
def html(*meta: str) -> str:
    """Construct the base html string based on additional tags and flags."""

    new_line = '\n        '
    meta = [META[tag] for tag in meta if tag in META]

    new_line = "\n"
    addons = f'{new_line + new_line.join(meta) if len(meta) > 0 else ""}'
    addons += "\n" + f'<link rel="shortcut icon" href="{url(CONFIG.build.favicon)}" type="image/x-icon">'

    return f"""\
<!DOCTYPE html>
<html lang="en">

    <head>{addons}
        <title>{{title or ''}}</title>
    </head>

    <body>
        <slot />
    </body>

</html>\
"""

REGEX = {
    "page": {
        "name": re.compile(r"(page)(@)?([a-zA-Z]+)?(.phml)")
    },    
    "layout": {
        "name": re.compile(r"(layout)(@)?([a-zA-Z]+)?(.phml)")
    },
    "file": {
        "name": re.compile(r"([a-zA-Z_0-9]+)(@)?([a-zA-Z]+)?(\.[a-z]{,4})")
    },
    "group": {
        "name": re.compile(r"\(([a-zA-Z0-9]+)\)"),
        "path": {
            "start": re.compile(r"\([a-zA-Z0-9]+\)\/"),
            "middle": re.compile(r"\/\([a-zA-Z0-9]+\)\/"),
        }
    }
}

def get_group_name(group: str) -> str:
    """Get the group name from the format `(name)`."""
    name = REGEX["group"]["name"].match(group)
    if name is not None:
        return name.group(1)
    return ""

def first(condition: Callable, collection: list | dict | tuple) -> Any:
    """Find the first match given the condition.

    Return:
        Any | None: The found value or None if no value was found.
    """
    if isinstance(collection, dict):
        for value in collection.values():
            if condition(value):
                return value
    else:
        for value in collection:
            if condition(value):
                return value
    return None

def title(text: str | list[str]) -> str:
    """Generate the title case version of the passed in text."""
    tokens = text
    if isinstance(text, str):
        tokens = text.split(" ")
    return " ".join([token[0].upper() + token[1:] for token in tokens])
