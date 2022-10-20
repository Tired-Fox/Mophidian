from __future__ import annotations


from os import path
from json import load

from .types import Markdown, Site, Build, Integration


class Config:
    def __init__(self, path_: str = ""):
        if len(path_) > 0 and path.isfile(path_):
            with open(path_, "r", encoding="UTF-8") as cfx:
                self._cfg_raw = load(cfx)
        else:
            for conf_file in ["moph.json", "mophidian.json", "conf.json", "config.json"]:
                if path.isfile(conf_file):
                    with open(conf_file, "r", encoding="UTF-8") as cfx:
                        self._cfg_raw = load(cfx)
                    break

        self.errors = []

        # Import and validate markdown section of config
        self.markdown = None
        if Markdown.key() in self._cfg_raw:
            self.markdown = Markdown(**self._cfg_raw["markdown"])
            if self.markdown.has_errors():
                self.errors.append(self.markdown.format_errors())

        # Import and validate site section
        self.site = None
        if Site.key() in self._cfg_raw:
            self.site = Site(**self._cfg_raw["site"])
            if self.site.has_errors():
                self.errors.append(self.site.format_errors())

        # Import and validate build section
        self.build = None
        if Build.key() in self._cfg_raw:
            self.build = Build(**self._cfg_raw["build"])
            if self.build.has_errors():
                self.errors.append(self.build.format_errors())

        self.integration = None
        if Integration.key() in self._cfg_raw:
            self.integration = Integration(**self._cfg_raw["integration"])
            if self.integration.has_errors():
                self.errors.append(self.integration.format_errors())
        else:
            self.integration = Integration()

        self.print_errors()

    def print_errors(self):
        from util import FColor, Style, color, RESET

        if len(self.errors) > 0:
            print(
                color(
                    "[",
                    color("IMPORTANT", prefix=[FColor.MAGENTA]),
                    "]",
                    prefix=[Style.BOLD],
                    suffix=[RESET],
                ),
                "These errors were found while loading the config:",
            )

            for error in self.errors:
                print(error)
                print()
