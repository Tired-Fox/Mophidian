from __future__ import annotations

from teddecor.decorators import config, TypesDefault


if __name__ == "__main__":

    @config(load="./markdown.json", save="markdown.json")
    class Markdown:
        """Mophidian.markdown configuration."""

        extensions = TypesDefault(
            list,
            nested_types=[str],
            default=[
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
            ],
        )
        """The markdown extensions that are to be used for every markdown file."""

        extension_configs = {
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

    @config(save="./config.json")
    class Config:
        """Some docstring"""

        markdown = Markdown
        endo = 1000

    cfg = Config.init()
    print(cfg)
