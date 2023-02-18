from __future__ import annotations
from pathlib import Path

from tcfg import cfg, TypesDefault
from saimll import Logger, SAIML

__all__ = [
    "Pygmentize",
    "MarkdownWrapper",
    "Markdown",
    "Site",
    "Build",
    "Config"
]

default_extensions = set((
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
))

default_extension_configs = {
        "footnotes": {
            "BACKLINK_TEXT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 384 512\" \
class=\"fn-backlink\" style=\"width: .75rem; height: .75rem;\" fill=\"currentColor\"><!--! \
Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - \
https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->\
<path d=\"M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 \
12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 \
12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z\"/></svg>"
        },
        "codehilite": {"css_class": "highlight"},
}

@cfg.yaml
class Pygmentize:
    """Mophidian.markdown.pygmentize configuration."""

    highlight = True
    """(bool) Whether to include the highlight css in the head."""

    path = "highlight.css"
    """(str) Path of where to generate the pygmentize css file."""

@cfg.yaml
class MarkdownWrapper:
    """Mophidian.markdown.wrapper configuration."""

    tag = "article"
    """(str) Tag of the element that wraps the markdown."""

    attributes = { "*": TypesDefault(str, list) }
    """(dict[str, str | list]) The attributes to apply to the markdown wrapper element."""

@cfg.yaml
class Markdown:
    """Mophidian.markdown configuration."""

    wrapper = MarkdownWrapper

    pygmentize = Pygmentize

    override_defaults = False
    """(bool) Flag for overriding default extensions and extension configs. Default allows
    adding to extensions list and overriding existing default extension configs. If
    True then only use what is provided in the config.
    """

    extensions = [
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
    """(list[str]) The markdown extensions that are to be used for every markdown file."""

    extension_configs = {
        "*": dict,
        "footnotes": {
            "BACKLINK_TEXT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 384 512\" \
class=\"fn-backlink\" style=\"width: .75rem; height: .75rem;\" fill=\"currentColor\"><!--! \
Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - \
https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->\
<path d=\"M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 \
12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 \
12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z\"/></svg>"
        },
        "codehilite": {"css_class": "highlight"},
    }
    """(dict[str, dict]) The configurations for each markdown extension."""


@cfg.yaml
class Site:
    """Mophidian.site configuration."""

    name = ""
    """(str) The name of the site. Defaults to `Mophidian`"""

    description = ""
    """(str) The websites description."""

    base_url = ""
    """Base url for the website. Example: https://{user}.github.io/"""

    version = "1.0"
    """(str) The version of the site `ex`: 0.1 or 1. Defaults to `1.0`"""

    source = "src/pages/"
    """(str) The directory to use for the source files."""

    components = "src/components/"
    """(str) The directory to use for the component files."""

    public = "public/"

    dest = "out/"
    """(str) The directory to put the built files into. Defaults to `site/`"""

    root = ""
    """(str) Root directory of the website. Used for links. Ex: `https://user.github.io/project/` where
    `project/` is the directory of the website. Defaults to ``
    """

    meta_tags = ["charset", "http_equiv", "viewport"]
    """(list["charset"|"http_equiv"|"viewport"]) Which default meta tags should mophidian include
    in the base page head tag.

    Tags:
        'charset': `<meta charset="UTF-8">`
        'http_equiv': `<meta http-equiv="X-UA-Compatible" content="IE=edge">`
        'viewport': `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
    """

@cfg.yaml
class RSSImage:
    title = ""
    """Image title"""
    url = ""
    """Image url"""
    width = 31
    """Image width. Max of 144"""
    height = 88
    """Image height. Max of 400"""

@cfg.yaml
class RSS:
    enabled = False
    """(bool) Toggle to generate a rss feed on build and expose the link to the pages."""

    paths = [str]
    """(list[str]) Paths of what markdown files to use for the rss feed. If no paths are specified then all
    rendered markdown files are added to the rss feed."""
    
    image = RSSImage
    """Mophidian.build.rss.image configuration"""
    
    language = "en-us"
    """(str) The language associated with the rss feed. Example: en-us."""


@cfg.yaml
class Sitemap:
    enabled = False
    """(bool) Toggle to generate a sitemap on build."""

    patterns = [str]
    """(list[str]) If you have a large site you may specify patters to apply. Each pattern is computed into it's
    own sitemap and referenced in a sitemap index. If no patterns are specified then a single
    sitemap is generated for all rendered pages."""


@cfg.yaml
class Build:
    """Mohpidian.build configuration."""

    refresh_delay = 2.0
    """(float) The delay until the live server reloads the browser after a file change is detected.
    Defaults to `2.0`.
    """

    sitemap = Sitemap
    """Mophidian.build.sitemap configuration"""

    rss = RSS
    """Mophidian.build.rss configuration"""

    favicon = "/favicon.ico"
    """(str) Path to the favicon from website root."""

    body = { "*": TypesDefault(str, list) }
    """(dict[str, str | list]) The attributes to apply to the body tag."""

    html = { "*": TypesDefault(str, list) }
    """(dict[str, str | list]) The attributes to apply to the html tag."""

class Config:
    """Mophidian configuration."""

    markdown = Markdown
    """Markdown configuration."""

    site = Site
    """Site configuration."""

    build = Build
    """Build configuration."""

def build_config(_type: str = ".yaml", data: dict | None = None):
    if _type in [".yml", ".yaml"]:
        @cfg.yaml(load_save=f"./moph{_type}")
        class YamlConfig(Config):
            pass
        return YamlConfig(data)
    elif _type == ".toml":
        @cfg.toml(load_save="./moph.toml")
        class TomlConfig(Config):
            pass
        return TomlConfig(data)
    else:
        @cfg.json(load_save="./moph.json")
        class JsonConfig(Config):
            pass
        return JsonConfig(data)

valid_files = ("moph.json", "moph.toml", "moph.yaml", "moph.yml",)
configs = [file for files in [Path("./").glob(e) for e in valid_files] for file in files]

if len(configs) > 1:
    config_files = ", ".join(SAIML.parse(f"'[@Fred$]{file}[]'") for file in configs)
    Logger.Error(f"More than one config found: {config_files}")
    exit()
elif len(configs) == 0:
    CONFIG = build_config(".yaml", {})
else:
    CONFIG = build_config(configs[0].suffix)
    
if CONFIG.markdown.extensions != default_extensions:
    for extension in CONFIG.markdown.extensions:
        default_extensions.add(extension)
    CONFIG.markdown.extensions = list(default_extensions)

if CONFIG.markdown.extension_configs != default_extension_configs:
    default_extension_configs.update(CONFIG.markdown.extension_configs)
    CONFIG.markdown.extension_configs = default_extension_configs
