from __future__ import annotations

from typing import Literal

from tcfg import Path, cfg

__all__ = ["Pygmentize", "MarkdownWrapper", "Markdown", "Site", "Build", "Config"]

default_extensions = {
    "abbr",
    "admonition",
    "attr_list",
    "def_list",
    "footnotes",
    "md_in_html",
    "tables",
    "toc",
    "wikilinks",
    "codehilite",
    "pymdownx.betterem",
    "pymdownx.caret",
    "pymdownx.details",
    "pymdownx.mark",
    "pymdownx.smartsymbols",
    "pymdownx.superfences",
    "pymdownx.tabbed",
    "pymdownx.tasklist",
    "pymdownx.tilde",
}

default_extension_configs = {
    "footnotes": {
        "BACKLINK_TEXT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" \
class="fn-backlink" style="width: .75rem; height: .75rem;" fill="currentColor"><!--! \
Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - \
https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->\
<path d="M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 \
12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 \
12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z"/></svg>'
    },
    "codehilite": {"css_class": "highlight"},
}


class Pygmentize(cfg):
    """Mophidian.markdown.pygmentize configuration."""

    highlight: bool = True
    """Whether to include the highlight css in the head."""

    path: str = "highlight.css"
    """Path of where to generate the pygmentize css file."""


class MarkdownWrapper(cfg):
    """Mophidian.markdown.wrapper configuration."""

    tag: str = "article"
    """Tag of the element that wraps the markdown."""

    attributes: dict[str, list]
    """The attributes to apply to the markdown wrapper element."""


class Markdown(cfg):
    """Mophidian.markdown configuration."""

    wrapper: MarkdownWrapper

    pygmentize: Pygmentize

    override_defaults: bool = False
    """Flag for overriding default extensions and extension configs. Default
    allows adding to extensions list and overriding existing default extension
    configs. If True then only use what is provided in the config.
    """

    extensions: list[str] = [
        "abbr",
        "admonition",
        "attr_list",
        "def_list",
        "footnotes",
        "md_in_html",
        "tables",
        "toc",
        "wikilinks",
        "codehilite",
        "pymdownx.betterem",
        "pymdownx.caret",
        "pymdownx.details",
        "pymdownx.mark",
        "pymdownx.smartsymbols",
        "pymdownx.superfences",
        "pymdownx.tabbed",
        "pymdownx.tasklist",
        "pymdownx.tilde",
    ]
    """The markdown extensions that are to be used for every markdown file."""

    extension_configs: dict[str, dict] = {
        "footnotes": {
            "BACKLINK_TEXT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" \
class="fn-backlink" style="width: .75rem; height: .75rem;" fill="currentColor"><!--! \
Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - \
https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->\
<path d="M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 \
12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 \
12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z"/></svg>'
        },
        "codehilite": {"css_class": "highlight"},
    }
    """The configurations for each markdown extension."""


class Site(cfg):
    """Mophidian.site configuration."""

    name: str = ""
    """The name of the site. Defaults to `Mophidian`"""

    description: str = ""
    """The websites description."""

    url: str = ""
    """Base url for the website. Example: https://{user}.github.io/"""

    version: str = "1.0"
    """The version of the site `ex`: 0.1 or 1. Defaults to `1.0`"""

    source: str = Path("src/pages/")
    """The directory to use for the source files."""

    components: str = Path("src/components/")
    """The directory to use for the component files."""

    public: str = Path("public/")

    dest: str = Path("out/")
    """The directory to put the built files into. Defaults to `site/`"""

    root: str = Path("")
    """Root directory of the website. Used for links.
    Ex: `https://user.github.io/project/` where `project/` is the directory of
    the website. Defaults to ``
    """

    meta_tags: list[Literal["charset", "http_equiv", "viewport"]] = [
        "charset",
        "http_equiv",
        "viewport",
    ]
    """Which default meta tags should mophidian include
    in the base page head tag.

    Tags:
        'charset': `<meta charset="UTF-8">`
        'http_equiv': `<meta http-equiv="X-UA-Compatible" content="IE=edge">`
        'viewport': `<meta name="viewport" content="width=device-width,
            initial-scale=1.0">`
    """


# class RSSImage(cfg):
#     """Mophidian.build.rss.image configuration."""

#     title: str = ""
#     """Image title"""
#     url: str = ""
#     """Image url"""
#     width: int = 31
#     """Image width. Max of 144"""
#     height: int = 88
#     """Image height. Max of 400"""


# class RSS(cfg):
#     """Mophidian.build.rss configuration."""

#     enabled: bool = False
#     """Toggle to generate a rss feed on build and expose the link to the pages.
#     """

#     paths: list[str]
#     """Paths of what markdown files to use for the rss feed. If no paths are
#     specified then all rendered markdown files are added to the rss feed."""

#     image: RSSImage
#     """Mophidian.build.rss.image configuration"""

#     language: str = "en-us"
#     """(str) The language associated with the rss feed. Example: en-us."""


# class Sitemap(cfg):
#     """Mophidian.build.sitemap configuration."""

#     enabled: bool = False
#     """Toggle to generate a sitemap on build."""

#     patterns: list[str]
#     """If you have a large site you may specify patters to apply. Each pattern
#     is computed into it's own sitemap and referenced in a sitemap index. If no
#     patterns are specified then a single sitemap is generated for all rendered
#     pages.
#     """

class Scripts(cfg):
    """Mophidian.build.scripts configuration"""

    pre: list[str]
    """List of commands to run, in cwd, before the initial build process."""

    post: list[str]
    """List of commands to run, in cwd, after the initial build process."""

class Build(cfg):
    """Mophidian.build configuration."""

    refresh_delay: float = 2.0
    """The delay until the live server reloads the browser after a file change
    is detected. Defaults to `2.0`.
    """

    scripts: Scripts
    # sitemap: Sitemap
    # """Mophidian.build.sitemap configuration"""

    # rss: RSS
    # """Mophidian.build.rss configuration"""

    favicon: str = Path("/favicon.ico")
    """Path to the favicon from website root."""

    body: dict[str, str | list[str]]
    """The attributes to apply to the body tag."""

    html: dict[str, str | list[str]]
    """The attributes to apply to the html tag."""


class Config(cfg):
    """Mophidian configuration."""

    _path_ = "moph.yml"

    markdown: Markdown
    """Markdown configuration."""

    site: Site
    """Site configuration."""

    build: Build
    """Build configuration."""

    data: str = "\x1b[33m"


CONFIG = Config()

if CONFIG.markdown.extensions != default_extensions:
    for extension in CONFIG.markdown.extensions:
        default_extensions.add(extension)
    CONFIG.markdown.extensions = list(default_extensions)

if CONFIG.markdown.extension_configs != default_extension_configs:
    default_extension_configs.update(CONFIG.markdown.extension_configs)
    CONFIG.markdown.extension_configs = default_extension_configs
