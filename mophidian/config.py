from tcfg import Option, cfg, new, PathType


def merge(dest: dict, source: dict):
    """Merge a dictionary into another dictionary. Only adding keys that don't already exist. It
    will only replace the deepest keys.

    Note:
        The method mutates the destination dict.
    """
    for key, value in source.items():
        if key in dest:
            if type(value) != type(dest[key]):
                dest[key] = value
            elif not isinstance(value, dict):
                dest[key] = value
            elif isinstance(value, dict):
                merge(dest[key], value)
        else:
            dest[key] = value


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


class Paths(cfg):
    files: PathType = new("src/pages")
    """Where the main pages for the website are located."""
    public: PathType = new("public")
    """Where public/static files are located."""
    components: PathType = new("src/components")
    """Where component files are located."""
    scripts: PathType = new("scripts")
    """Where python script files are located."""
    favicon: PathType = new("src/favicon.ico")
    out: PathType = new("out")
    """Where the built files will be written."""


class Pygmentize(cfg):
    """Mophidian.markdown.pygmentize configuration."""

    highlight: bool = True
    """Whether to include the highlight css in the head."""

    path: str = "highlight.css"
    """Path of where to generate the pygmentize css file. This should be the url path to the css file."""


class Site(cfg):
    site_name: str
    """Website name. This is exposed to the compiler."""

    base: PathType
    """Base website path. For example if you plan to deploy to github pages,
    you will have to use the project name as the base folder of the website.
    Ex: `/<project/`. Slashes are optional, but this will be used while compiling
    urls inside the website.
    """


class MarkdownWrapper(cfg):
    tag: str = "article"
    """The html tag to use to wrap the compiled markdown."""

    attributes: dict[str, bool | list | str]
    """Attributes to add to the markdown wrapper."""


class Markdown(cfg):
    wrapper: MarkdownWrapper
    """Compiled markdown wrapper tag configuration."""

    pygmentize: Pygmentize

    override_defaults: bool = False
    """Flag for overriding default extensions and extension configs. Default
    allows adding to extensions list and overriding existing default extension
    configs. If True then only use what is provided in the config.
    """

    extensions: set[str] = {
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
    """The markdown extensions that are to be used for every markdown file."""

    configs: dict[str, dict] = {
        "footnotes": {
            "BACKLINK_TEXT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512" \
class="fn-backlink" style="width: .75rem; height: .75rem;" fill="currentColor"><!--! \
Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - \
https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. -->\
<path d="M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 \
12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 \
12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z"/></svg>'
        },
        "codehilite": {"css_class": "code-highlight"},
    }
    """The configurations for each markdown extension."""


class Commands(cfg):
    pre: list[dict[str, str]]
    post: list[dict[str, str]]


class Build(cfg):
    meta_tags: set[Option["charset", "http-equiv", "viewport"]] = {
        "charset",
        "http-equiv",
        "viewport",
    }
    """Which default meta tags should mophidian include
    in the base page head tag.

    Tags:
        'charset': `<meta charset="UTF-8">`
        'http-equiv': `<meta http-equiv="X-UA-Compatible" content="IE=edge">`
        'viewport': `<meta name="viewport" content="width=device-width,
            initial-scale=1.0">`
    """

    commands: Commands
    """Extra commands to run pre build and post build."""


class Config(cfg):
    """Mophidian configuration."""

    _path_ = "src/moph.yml"

    paths: Paths
    """Paths for different file system operations."""
    site: Site
    """General site settings. These are exposed to the phml compiler."""
    markdown: Markdown
    """Markdown plugin configuration."""
    build: Build


CONFIG = Config()

if CONFIG.markdown.override_defaults:
    for extension in CONFIG.markdown.extensions:
        default_extensions.add(extension)
    merge(default_extension_configs, CONFIG.markdown.configs)

    CONFIG.markdown.extensions = default_extensions
    CONFIG.markdown.configs = default_extension_configs
