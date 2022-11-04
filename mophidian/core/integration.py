from __future__ import annotations
import contextlib

from functools import cached_property
from json import load
from pathlib import Path
import sys
from typing import Callable, Optional, TextIO
from teddecor import TED

from mophidian.core.config.config import Config
from .ppm import PPM
from moph_log import Log
from .snippets import snippets


__all__ = [
    "Tailwindcss",
    "Sass",
]


class Integration:
    """Base class for integrations. Allows for installation,
    checking for installed packages, and setting up integrations.
    """

    def __init__(self, logger: Log, pkgm: PPM, ostdo: TextIO, ostde: TextIO):
        self.logger = logger
        self.pkgm = pkgm
        self.link = ""
        self.old_stdo = ostdo
        self.old_stde = ostde

    @classmethod
    def build(
        cls,
        package: str,
        logger: Log,
        pkgm: PPM,
        ostdo: TextIO = sys.stdout,
        ostde: TextIO = sys.stderr,
    ) -> Tailwindcss | Sass | None:
        """"""
        package = package.lower()
        if package == "tailwindcss":
            return Tailwindcss(logger, pkgm)
        elif package == "sass":
            return Sass(logger, pkgm, ostdo, ostde)
        else:
            return None

    @cached_property
    def has_addons(self) -> bool:
        """Check if a integration has addons."""

        return hasattr(self, "addons") and len(getattr(self, "addons")) > 0

    @cached_property
    def addon_names(self) -> list[str]:
        """Get the addon names for the integration."""

        if hasattr(self, "addons"):
            return [addon.name for addon in getattr(self, "addons")]
        else:
            return []

    def addon(self, addon: str) -> str:
        """Get a package name for a given addon."""

        if addon in self.addon_names:
            return f"@{self.__class__.__name__.lower()}/{addon}"
        else:
            raise IndexError(f"{addon} is not a plugin/addon for {self.__class__.__name__.lower()}")

    @cached_property
    def name(self) -> str:
        """Name of the integration."""
        return self.__class__.__name__.lower()

    def installed(self, package: str) -> bool:
        """Check if a certain package is installed.
        Will also automatically init a package.json if needed.

        Args:
            package (str): The package to check for installation.

        Returns:
            bool: True if installed, else False
        """

        path_pkg_json = Path("package.json")
        modules = Path("node_modules")
        if path_pkg_json.exists():
            if modules.exists():
                with open("package.json", "r", encoding="utf-8") as package_json:
                    pkg_json = load(package_json)

                if "devDependencies" in pkg_json:
                    if package in pkg_json["devDependencies"]:
                        # Package exists
                        return True

                if "dependencies" in pkg_json:
                    if package in pkg_json["dependencies"]:
                        # Package exists
                        return True

                return False
            else:
                return False
        else:
            self.logger.Info("package.json was not found")
            self.pkgm.ppm.init()
            return False

    def install(self, config: Config):
        """Install the integration and plugins/addons if applicable."""

        if self.pkgm.ppm.has_node:
            if self.link != "":
                self.logger.Custom(
                    "Find out more on the package",
                    TED.parse(f"[~{self.link}]{self.name}[~]"),
                    label="Link",
                )

            if not self.installed(self.name):
                self.pkgm.ppm.install(self.name, "-D")

            self.setup(config)

            if self.has_addons:
                self.require_addons()
        else:
            self.logger.Warning(
                "You do not have node.js installed.",
                TED.parse("[@F yellow]*Node.js"),
                "integrations will be skipped.",
            )

    def setup(self, config: Config):
        """Setup any additional requirements for this package."""

    def require_addons(self):
        """Ask user if they would like certain addons. Then install them and set them up."""


class Addon:
    """Defines a addon and it's associated information."""

    def __init__(self, name: str, desc: str, link: str):
        self.name = name
        self.desc = desc
        self.link = link

    def url(self, title: Optional[str] = None) -> str:
        """Formatted ansi link to the package link."""
        name = self.name if title is None else title
        return f"[~{self.link}]{name}[~]"

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"[~{self.link}]{self.name}[~] - {self.desc}"


class Sass(Integration):
    """Sass integration. Installs sass and adds compilation scripts to package.json."""

    def __init__(
        self,
        logger: Log,
        pkgm: PPM,
        ostdo: TextIO = sys.stdout,
        ostde: TextIO = sys.stderr,
    ):
        super().__init__(logger, pkgm, ostdo, ostde)
        self.link = "https://sass-lang.com/"

    def setup(self, config: Config):
        """Setup any additional requirements for this package."""

        self.logger.Debug("Adding sass scripts to package.json")
        self.logger.Debug(f"Added\n{snippets['sass_scripts']}")

        Path("styles/sass/").mkdir(parents=True, exist_ok=True)
        with open("./package.json", "r", encoding="utf-8") as package_json:
            from json import load, dumps

            pj = load(package_json)
            if "scripts" not in pj:
                pj["scripts"] = {}
            for script in snippets["sass_scripts"]:
                if not isinstance(snippets["sass_scripts"][script], Callable):
                    pj["scripts"].update({script: snippets["sass_scripts"][script]})
                else:
                    pj["scripts"].update(
                        {script: snippets["sass_scripts"][script](config.site.source)}
                    )

        with open("./package.json", "w", encoding="utf-8") as package_json:
            package_json.write(dumps(pj, indent=2))


class Tailwindcss(Integration):
    """Tailwindcss integration. Installs tailwindcss and adds
    compilation scripts to `package.json`.

    Will also add the `tailwind.config.js` file and auto
    install plugins after asking if the user wants them. These
    plugins are automatically added to the `tailwind.config.js` file.
    """

    def __init__(
        self,
        logger: Log,
        pkgm: PPM,
        ostdo: TextIO = sys.stdout,
        ostde: TextIO = sys.stderr,
    ):
        super().__init__(logger, pkgm, ostdo, ostde)
        self.link = "https://tailwindcss.com/"
        self.addons = [
            Addon(
                name="typography",
                desc="Beautiful typographic defaults for HTML you don't control.",
                link="https://tailwindcss.com/docs/typography-plugin",
            ),
            Addon(
                name="forms",
                desc="A plugin that provides a basic reset for form styles that makes form elements easy to override with utilities.",
                link="https://github.com/tailwindlabs/tailwindcss-forms",
            ),
            Addon(
                name="aspect-ratio",
                desc="A plugin that provides a composable API for giving elements a fixed aspect ratio.",
                link="https://github.com/tailwindlabs/tailwindcss-aspect-ratio",
            ),
            Addon(
                name="line-clamp",
                desc="A plugin that provides utilities for visually truncating text after a fixed number of lines.",
                link="https://github.com/tailwindlabs/tailwindcss-line-clamp",
            ),
            Addon(
                name="container-queries",
                desc="A plugin for Tailwind CSS v3.2+ that provides utilities for container queries.",
                link="https://github.com/tailwindlabs/tailwindcss-container-queries",
            ),
        ]

    def add_tailwind_scripts(self, config: Config):
        """Adds compilations scripts to `package.json`."""

        with open("./package.json", "r", encoding="utf-8") as package_json:
            from json import load, dumps

            pj = load(package_json)
            if "scripts" not in pj:
                pj["scripts"] = {}

            for script in snippets["tailwind_scripts"]:
                if not isinstance(snippets["tailwind_scripts"][script], Callable):
                    pj["scripts"].update({script: snippets["tailwind_scripts"][script]})
                else:
                    pj["scripts"].update(
                        {script: snippets["tailwind_scripts"][script](config.site.dest)}
                    )

        with open("./package.json", "w", encoding="utf-8") as package_json:
            package_json.write(dumps(pj, indent=2))

    def add_tailwind_css(self):
        """Add base tailwind.css file to project."""

        Path("styles").mkdir(parents=True, exist_ok=True)
        if not Path("./tailwind.css").exists():
            with open("./tailwind.css", "+w", encoding="utf-8") as tailwindcss:
                tailwindcss.write(snippets["tailwind_css"])

    def add_tailwind_config_open(self, config: Config):
        """Write out the first part of the `tailwind.config.js` file up to plugins section."""

        with open("tailwind.config.js", "+w", encoding="utf-8") as tcss_cfg:
            tcss_cfg.write(
                snippets["tailwind_config_open"](
                    config.site.dest.replace("\\", "/").lstrip("/").rstrip("/")
                )
            )

    def add_tailwind_config_close(self):
        """Add the closing part of the `tailwind.config.js` file."""

        with open("tailwind.config.js", "a", encoding="utf-8") as tcss_cfg:
            tcss_cfg.write(snippets["tailwind_config_close"])

    def add_tailwind_config_plugin(self, addon: Addon):
        """Add a tailwind plugins to the `tailwind.config.js` file."""

        with open("tailwind.config.js", "a", encoding="utf-8") as tcss_cfg:
            tcss_cfg.write(f'    require("@tailwindcss/{addon.name}"),\n')

    def update_refresh_delay(self):
        """Update the livereload server's refresh delay to account for tailwind build time."""

        if Path("moph.json").exists():
            with open("moph.json", "r", encoding="utf-8") as moph_config:
                cfg = load(moph_config)

            if "build" not in cfg:
                cfg["build"] = {}

            cfg["build"]["refresh_delay"] = 3

            with open("moph.json", "w", encoding="utf-8") as moph_config:
                from json import dumps

                moph_config.write(dumps(cfg, indent=2))

    def setup(self, config: Config):
        """Setup any additional requirements for this package."""

        self.add_tailwind_scripts(config)
        self.add_tailwind_css()
        self.update_refresh_delay()
        self.add_tailwind_config_open(config)

    def require_addons(self):
        """Ask user if they would like certain addons. Then install them and set them up."""

        self.logger.Message(
            TED.parse(
                "\[[@F green]*Y*[@F]\] yes, \[[@F blue]*A*[@F]\] all yes \[[@F red]*N*[@F]\] no \[[@F yellow]*D*[@F]\] all no"
            )
        )
        all_yes = False
        all_no = False
        for addon in self.addons:
            if not self.installed(f"@tailwindcss/{addon.name}"):
                install = False
                if not all_yes and not all_no:
                    with contextlib.redirect_stdout(self.old_stdo):
                        with contextlib.redirect_stderr(self.old_stde):
                            try:
                                install = input(
                                    TED.parse(
                                        f"*Would you like to install the {addon.url(title=f'@tailwindcss/{addon.name}')} plugin? \[[@F green]y[@F]:[@F blue]a[@F]:[@F red]n[@F]:[@F yellow]D[@F]\] "
                                    )
                                )
                            except KeyboardInterrupt:
                                install = "D"
                                all_no = True
                                print()

                    if install.lower() == "y":
                        install = True
                    elif install.lower() == "n":
                        install = False
                    elif install.lower() == "a":
                        install = True
                        all_yes = True
                    else:
                        install = False
                        all_no = True

                if install or all_yes:
                    self.pkgm.ppm.install(f"@tailwindcss/{addon.name}", "-D")
                    self.add_tailwind_config_plugin(addon)
            else:
                self.add_tailwind_config_plugin(addon)

        self.add_tailwind_config_close()
