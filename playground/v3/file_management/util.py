import re
from typing import Any, Callable


group_name_re = re.compile(r"\(([a-zA-Z0-9]+)\)")

def get_group_name(group: str) -> str:
    """Get the group name from the format `(name)`."""
    name = group_name_re.match(group)
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
