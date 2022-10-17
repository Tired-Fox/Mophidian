from __future__ import annotations


from os import path
from json import load, dumps
from pprint import pprint  #! DEBUG ONLY

from .types import Markdown


class Config:
    def __init__(self, path_: str = ""):
        if len(path_) > 0 and path.isfile(path_):
            with open(path_, "r", encoding="UTF-8") as cfx:
                self._cfx_raw = load(cfx)
        else:
            for conf_file in ["moph.json", "mophidian.json", "conf.json", "config.json"]:
                if path.isfile(conf_file):
                    with open(conf_file, "r", encoding="UTF-8") as cfx:
                        self._cfx_raw = load(cfx)
                    break

        self.errors = []

        self.markdown = None
        if Markdown.key() in self._cfx_raw:
            self.markdown = Markdown(**self._cfx_raw["markdown"])
            if self.markdown.has_errors():
                self.errors.append(self.markdown.format_errors())

            pprint(self.markdown.extensions)
            pprint(self.markdown.extension_configs)

        self.print_errors()

    def print_errors(self):
        from .types.util import Color, Style, color, RESET

        print(
            color(
                "These errors were found while loading the config:\n",
                prefix=[Color.MAGENTA, Style.BOLD],
            )
        )
        for error in self.errors:
            print(error)
            print()
