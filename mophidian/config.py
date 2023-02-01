from __future__ import annotations
from pathlib import Path

from teddecor.decorators import config, TypesDefault
from teddecor import Logger, TED


@config.yaml
class Pygmentize:
    """Mophidian.markdown.pygmentize configuration."""

    highlight = True
    """Whether to include the highlight css in the head."""

    path = "highlight.css"
    """Path of where to generate the pygmentize css file."""

@config.yaml
class MarkdownWrapper:
    """Mophidian.markdown.wrapper configuration."""

    tag = "article"
    """Tag of the element that wraps the markdown."""

    attributes = { "*": TypesDefault(str, list) }
    """The attributes to apply to the markdown wrapper element."""

@config.yaml
class Markdown:
    """Mophidian.markdown configuration."""

    wrapper = MarkdownWrapper

    pygmentize = Pygmentize

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
    """The markdown extensions that are to be used for every markdown file."""

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
    """The configurations for each markdown extension."""


@config.yaml
class Site:
    """Mophidian.site configuration."""

    name = ""
    """The name of the site. Defaults to `Mophidian`"""

    version = "1.0"
    """The version of the site `ex`: 0.1 or 1. Defaults to `1.0`"""

    source = "src/pages/"
    """The directory to use for the source files."""

    components = "src/components/"
    """The directory to use for the component files."""

    public = "public/"

    dest = "out/"
    """The directory to put the built files into. Defaults to `site/`"""

    root = ""
    """Root directory of the website. Used for links. Ex: `https://user.github.io/project/` where
    `project/` is the directory of the website. Defaults to ``
    """

    meta_tags = ["charset", "http_equiv", "viewport"]
    """Which default meta tags should mophidian include in the base page head tag.

    Tags:
        'charset': `<meta charset="UTF-8">`
        'http_equiv': `<meta http-equiv="X-UA-Compatible" content="IE=edge">`
        'viewport': `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
    """


@config.yaml
class Build:
    """Mohpidian.build configuration."""

    refresh_delay = 2.0
    """The delay until the live server reloads the browser after a file change is detected.
    Defaults to `2.0`.
    """

    favicon = "/favicon.ico"
    """Path to the favicon from website root."""

    body = { "*": TypesDefault(str, list) }
    """The attributes to apply to the body tag."""

    html = { "*": TypesDefault(str, list) }
    """The attributes to apply to the html tag."""

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
        @config.yaml(load_save=f"./moph{_type}")
        class YamlConfig(Config):
            pass
        return YamlConfig(data)
    elif _type == ".toml":
        @config.toml(load_save="./moph.toml")
        class TomlConfig(Config):
            pass
        return TomlConfig(data)
    else:
        @config.json(load_save="./moph.json")
        class JsonConfig(Config):
            pass
        return JsonConfig(data)

valid_files = ("moph.json", "moph.toml", "moph.yaml", "moph.yml",)
configs = [file for files in [Path("./").glob(e) for e in valid_files] for file in files]

if len(configs) > 1:
    config_files = ", ".join(TED.parse(f"'[@Fred$]{file}[]'") for file in configs)
    Logger.error(f"More than one config found: {config_files}").flush()
    exit()
elif len(configs) == 0:
    Logger.warning("No config file found, generating default yaml config").flush()
    CONFIG = build_config(".yaml", {})
else:
    CONFIG = build_config(configs[0].suffix)
