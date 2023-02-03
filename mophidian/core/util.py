from __future__ import annotations
import re
from functools import cache

from mophidian.config import CONFIG

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