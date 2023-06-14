from functools import cache
from pathlib import Path
from subprocess import run

from saimll import Logger
from mophidian.config import CONFIG
from mophidian.pygmentize import generate_highlight

META = {
    "charset": '<meta charset="UTF-8">',
    "http_equiv": '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
    "viewport": '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
}


def url(url: str) -> str:
    """Construct a url given a page url and the project's rool."""

    root = f"/{CONFIG.site.base.strip('/')}/" if CONFIG.site.base != "" else ""
    return root + url.lstrip("/")


@cache
def html() -> str:
    new_line = "\n        "
    _meta = [META[tag] for tag in CONFIG.build.meta_tags if tag in META]

    new_line = "\n"
    addons = f'{new_line + new_line.join(_meta) + new_line if len(_meta) > 0 else ""}'
    links = (
        "\n"
        + f'<link rel="shortcut icon" href="{url(CONFIG.paths.favicon)}" type="image/x-icon">'
    )

    if CONFIG.markdown.pygmentize.highlight:
        if (
            not (
                Path(CONFIG.paths.public) / CONFIG.markdown.pygmentize.path.strip("/")
            ).is_file()
            and not (
                Path(CONFIG.paths.files) / CONFIG.markdown.pygmentize.path.strip("/")
            ).is_file()
        ):
            Logger.Warning("No Pygmentize css file found")
            generate_highlight("one-dark")
            Logger.Info("Use 'moph highlight <style>' to generate a new Pygmentize css file with a custom style")

        links += (
            f'\n<link rel="stylesheet" href="{url(CONFIG.markdown.pygmentize.path)}">'
        )

    return f"""\
<!DOCTYPE html>
<html lang="en">

    <head>{addons}{links}
        <title>{{{{title or ''}}}}</title>
    </head>

    <body>
        <Slot />
    </body>

</html>\
"""
