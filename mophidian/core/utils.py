import functools
import os
from pathlib import Path, PurePath
import re
import shutil
from typing import TYPE_CHECKING, Any, Optional

from jinja2 import Environment, Template
from .config.config import Config
from .toc import TOC


from markdown import Markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import AMP_SUBSTITUTE
from xml.etree.ElementTree import Element
from urllib.parse import urlsplit, urlunsplit, unquote
import posixpath
from moph_log import Logger

if TYPE_CHECKING:
    from .navigation import Nav


def build_template_dict(templates: Environment) -> dict[str, dict | Template]:
    result = {}
    for cmpt in templates.list_templates():
        path = PurePath(cmpt)
        name = path.name.replace(path.suffix, "")
        breadcrumbs = path.as_posix().replace(path.suffix, "").split("/")[:-1]

        current = result
        failed = False
        for crumb in breadcrumbs:
            if crumb not in current:
                current[crumb] = {}
            if not isinstance(current[crumb], Template):
                current = current[crumb]
            else:
                failed = True
                break

        if not failed:
            current.update({name: templates.get_template(path.as_posix())})

    return result


def copy_file(source_path: str, output_path: str) -> None:
    """
    Copy source_path to output_path, making sure any parent directories exist.
    The output_path may be a directory.
    """
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    if os.path.isdir(output_path):
        output_path = output_path.join(PurePath(source_path).name)
    shutil.copyfile(source_path, output_path)


Meta = dict[str, Any]
Content = str
HTML = str


def renderTemplate(
    page,
    nav,
    config: Config,
    components: dict[str, dict | Template],
    layouts: dict[str, dict | Template],
) -> HTML:
    """Render the html file as a jinja2.Template exposing useful data.

    Args:
        page (Page): HTML page that is being rendered
        nav (Nav): Iterable navigation object
        config (Config): Config object for extra logic and data
        components (dict[str, dict | Template]): Dict of jinja2.Template componenets
        layouts (dict[str, dict | Template]): Dict of jinja2.Template layouts

    Returns:
        HTML: Rendered html as a string
    """
    if page.content is not None:
        environment = Environment()
        layout = environment.from_string(page.content)
        params = {
            "cmpt": components,
            "lyt": layouts,
            "meta": page.meta,
            "nav": nav,
            "site": config.site,
        }
        return layout.render(**params, page=page)

    return ""


class MophidianMarkdown:
    """A collection of functions to parse and handle markdown.

    Third-Party Packages:
        - markdown: Parses markdown with plugins
        - pymdown-extensions: Adds additional maintained plugins
        - python-frontmatter: Parses yaml frontmatter from the file
    """

    @classmethod
    def get_title(cls, markdown: str) -> Optional[str]:
        """Extract the documents title from the header 1.

        Args:
            markdown (str): The markdown to parse

        Returns:
            str: The title parsed from the markown string
        """
        lines = markdown.split('\n')
        if len(lines) > 0 and re.match(r"[ \t]*#{1}[^#]+", lines[0]) is not None:
            return lines[0].strip().lstrip("#")
        elif len(lines) > 1 and re.match(r"[ \t]*=+[\s\t]+", lines[1]) is not None:
            return lines[0].strip()
        return None

    @classmethod
    def parse(
        cls, file: str, config: Config, layouts: dict[str, dict | Template], template=None
    ) -> tuple[Meta, Content]:
        """Parse the metadata from the markdown content.

        Args:
            file (str): The file content as a string.
            config (Config): Mophidian config for extra logic.

        Returns:
            tuple[Meta, Content]: Returns the meta data as a dict and the content as a string.
        """
        import frontmatter

        meta, content = frontmatter.parse(file)

        def get_layout(path: str):
            pl = path.split(".")
            current = layouts
            failed = False
            for token in pl[:-1]:
                if token in current and not isinstance(current[token], Template):
                    current = current[token]
                else:
                    failed = True
                    break

            if not failed and pl[-1] in current:
                return current[pl[-1]]
            else:
                return None

        meta: Meta = meta
        content: Content = content

        layout = None

        if template is None:
            # If markdown page specified a layout
            if 'layout' in meta:
                template = get_layout(meta['layout'])

            # If no layout then attempt to retrive config default
            if template is None:
                template = get_layout(config.build.default_layout)
                # If config default is invalid then use the provided default layout
                if template is None:
                    template = layouts["moph_base"]

        return meta, content

    @classmethod
    def render(
        cls,
        page,
        nav,
        config: Config,
        components: dict[str, dict | Template],
        layouts: dict[str, dict | Template],
        files,
        contents,
    ) -> tuple[HTML, TOC]:
        """Render the markdown content to html. Mophidian will expose a few things to the pages template while compiling. It will expose components and layouts as jinja2.Templates. It will also expose the meta data, site data from the config, and the navigation data.

        Args:
            page (Page): The page that is being rendered
            nav (Nav): The navigation data
            config (Config): The config data that influences logic
            components (dict[str, Template]): Dict of jinja2.Template components
            layouts (dict[str, Template]): Dict of jinja2.Template layouts

        Returns:
            HTML: Renders html as a string
        """
        from .toc import build_toc

        html = ""
        toc = TOC([])
        if page.markdown is not None:
            params = {
                "cmpt": components,
                "lyt": layouts,
                "meta": page.meta,
                "nav": nav,
                "site": config.site,
            }

            # convert markdown content to html content
            md = Markdown(
                extensions=[
                    _RelativePathExtension(page.file, files, contents),
                    *config.markdown.extensions,
                ],
                extension_configs=config.markdown.extension_configs,
            )
            content = md.reset().convert(page.markdown)

            if page.template:
                toc = build_toc(getattr(md, 'toc_tokens', []))
                html = page.template.render(**params, content=content, page=page, toc=toc)

        return html, toc


@functools.lru_cache(maxsize=None)
def _norm_parts(path: str) -> list[str]:
    if not path.startswith('/'):
        path = '/' + path
    path = posixpath.normpath(path)[1:]
    return path.split('/') if path else []


def get_relative_url(url: str, other: str) -> str:
    """
    Return given url relative to other.
    Both are operated as slash-separated paths, similarly to the 'path' part of a URL.
    The last component of `other` is skipped if it contains a dot (considered a file).
    Actual URLs (with schemas etc.) aren't supported. The leading slash is ignored.
    Paths are normalized ('..' works as parent directory), but going higher than the
    root has no effect ('foo/../../bar' ends up just as 'bar').
    """
    # Remove filename from other url if it has one.
    dirname, _, basename = other.rpartition('/')
    if '.' in basename:
        other = dirname

    other_parts = _norm_parts(other)
    dest_parts = _norm_parts(url)
    common = 0
    for a, b in zip(other_parts, dest_parts):
        if a != b:
            break
        common += 1

    rel_parts = ['..'] * (len(other_parts) - common) + dest_parts[common:]
    relurl = '/'.join(rel_parts) or '.'
    return relurl + '/' if url.endswith('/') else relurl


def url_relative_to(current: str, other: str) -> str:
    """Return url for file relative to other file."""
    return get_relative_url(current, other)


class _RelativePathTreeprocessor(Treeprocessor):
    def __init__(self, file, files, contents) -> None:
        self.file = file
        self.files = files
        self.contents = contents

    def run(self, root: Element) -> Element:
        """
        Update urls on anchors and images to make them relative
        Iterates through the full document tree looking for specific
        tags and then makes them relative based on the site navigation
        """
        for element in root.iter():
            if element.tag == 'a':
                key = 'href'
            elif element.tag == 'img':
                key = 'src'
            else:
                continue

            url = element.get(key)
            assert url is not None
            new_url = self.path_to_url(url)
            element.set(key, new_url)

        return root

    def path_to_url(self, url: str) -> str:
        scheme, netloc, path, query, fragment = urlsplit(url)

        if (
            scheme
            or netloc
            or not path
            or url.startswith('/')
            or url.startswith('\\')
            or AMP_SUBSTITUTE in url
            or '.' not in os.path.split(path)[-1]
        ):
            # Ignore URLs unless they are a relative link to a source file.
            # AMP_SUBSTITUTE is used internally by Markdown only for email.
            # No '.' in the last part of a path indicates path does not point to a file.
            return url

        # Determine the filepath of the target.
        target_uri = posixpath.join(posixpath.dirname(self.file.src_uri), unquote(path))
        target_uri = posixpath.normpath(target_uri).lstrip('/')

        # Validate that the target exists.
        target_file = self.files.contains_src(target_uri)
        if target_file is None:
            target_file = self.contents.contains_src(target_uri)

        if not Path(target_uri).exists() and target_file is None:
            Logger.Warning(
                f"Documentation file '{self.file.src_uri}' contains a link to "
                f"'{target_uri}' which is not found in the files."
            )
            return url

        if target_file is not None:
            path = url_relative_to(target_file.url, self.file.url)
        else:
            path = url_relative_to(target_uri, self.file.url)

        components = (scheme, netloc, path, query, fragment)
        return urlunsplit(components)


class _RelativePathExtension(Extension):
    """
    The Extension class is what we pass to markdown, it then
    registers the Treeprocessor.
    """

    def __init__(self, file, files, contents) -> None:
        self.file = file
        self.files = files
        self.contents = contents

    def extendMarkdown(self, md: Markdown) -> None:
        relpath = _RelativePathTreeprocessor(self.file, self.files, self.contents)
        md.treeprocessors.register(relpath, "relpath", 0)
