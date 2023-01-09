import re
from typing import Any, Callable


html = """\
<!DOCTYPE html>
<html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
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
        "name": re.compile(r"(layout|page)(@)?([a-zA-Z]+)?(.phml)")
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
