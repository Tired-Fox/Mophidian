import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

from .pages import Page, Pages


def init_static():
    '''Remove old files from site folder. Then copy all static files to `site/`'''
    if os.path.isdir('site/'):
        shutil.rmtree('site/')
    if os.path.isdir('static/'):
        shutil.copytree('static/', 'site/')


# Filesturture looks like this
# {index,readme}.{html.md}
#   - [dir]
#       - {index,readme}.{html,md}
def find_pages() -> Pages:
    """Get all files in the `pages/` directory

    Returns:
        Pages: A collection of all the pages that were found.
    """
    pages = Pages()
    if os.path.isdir('pages'):
        for path in Path('pages').glob(f"./**/*.*"):
            if path.suffix in [".md", ".html"]:
                pages.append(Page(path.parent.as_posix(), path.name, path.suffix))
    return pages


def find_content() -> Pages:
    """Get all files in the `pages/` directory

    Returns:
        Pages: A collection of all the pages that were found."""
    content = Pages()
    if os.path.isdir('content'):
        for path in Path('content').glob(f"./**/*.md"):
            content.append(Page(path.parent.as_posix(), path.name, path.suffix))
    return content


def get_components() -> dict[str, Template]:
    """Get all jinja templates from `componenets/`.

    Returns:
        dict[str, Template]: Dictionary of all components (user defined)
    """
    components = {}
    if os.path.isdir('components'):
        for path in Path('components').glob(f"./**/*.html"):
            environment = Environment(loader=FileSystemLoader("./"))
            components.update(
                {path.name.replace(path.suffix, ""): environment.get_template(path.as_posix())}
            )
    return components


def get_layouts() -> dict[str, Template]:
    """Get all jinja layouts from `layouts/`

    Returns:
        dict[str, Template]: Dictionary of all layouts (user defined)
    """
    layouts = {}
    environment = Environment(loader=FileSystemLoader("./"))
    if os.path.isdir('layouts'):
        for path in Path('layouts').glob(f"./**/*.html"):
            layouts.update(
                {path.name.replace(path.suffix, ""): environment.get_template(path.as_posix())}
            )

    import pathlib

    built_in = pathlib.Path(__file__).parent.resolve().as_posix()
    environment = Environment(loader=FileSystemLoader(built_in))

    # Add default layout(s)
    layouts.update({"moph_base": environment.get_template("moph_base.html")})
    return layouts
