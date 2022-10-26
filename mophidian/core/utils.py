import os
from pathlib import Path, PurePath
import re
import shutil
from typing import TYPE_CHECKING, Any, Optional

from jinja2 import Environment, Template
from .config.config import Config
from .toc import TOC

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
        for line in markdown.split('\n'):
            if re.match(r"[ \t]*#{1}.+", line) is not None:
                return line.strip().lstrip("#")
        return None

    @classmethod
    def parse(
        cls, file: str, config: Config, layouts: dict[str, dict | Template]
    ) -> tuple[Meta, Content, Template]:
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

        # If markdown page specified a layout
        if 'layout' in meta:
            layout = get_layout(meta['layout'])

        # If no layout then attempt to retrive config default
        if layout is None:
            layout = get_layout(config.build.default_layout)
            # If config default is invalid then use the provided default layout
            if layout is None:
                layout = layouts["moph_base"]

        return meta, content, layout

    @classmethod
    def render(
        cls,
        page,
        nav,
        config: Config,
        components: dict[str, dict | Template],
        layouts: dict[str, dict | Template],
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
        from markdown import Markdown
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
                extensions=config.markdown.extensions,
                extension_configs=config.markdown.extension_configs,
            )
            content = md.reset().convert(page.markdown)

            if page.template:
                toc = build_toc(getattr(md, 'toc_tokens', []))
                html = page.template.render(**params, content=content, page=page, toc=toc)

        return html, toc
