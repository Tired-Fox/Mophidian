from __future__ import annotations
from cmath import log

from functools import cached_property
from json import load
from pathlib import Path
from ppm import PPM
from moph_logger import Log, LL, url, color, FColor, Style, RESET
from new.snippets import snippets


all = ["Tailwind", "Sass"]


def check_nodejs(logger: Log = None):
    from shutil import which
    from subprocess import check_output

    if which("node") is not None:
        if logger is not None:
            logger.Custom(
                f"Node {check_output(['node', '--version']).decode()}",
                clr=FColor.YELLOW,
                label="Version",
            )
    else:
        if logger is not None:
            logger.Error(
                "Node.js was not found. Install it and try again or disable all integrations."
            )
        exit(3)


class Integration:
    def __init__(self, logger: Log, pkgm: PPM):
        self.logger = logger
        self.pkgm = pkgm
        self.link = ""

    @classmethod
    def build(cls, package: str, logger: Log, pkgm: PPM) -> Tailwindcss | Sass | None:
        package = package.lower()
        if package == "tailwindcss":
            return Tailwindcss(logger, pkgm)
        elif package == "sass":
            return Sass(logger, pkgm)
        else:
            return None

    @cached_property
    def has_addons(self) -> bool:
        return hasattr(self, "addons") and len(getattr(self, "addons")) > 0

    @cached_property
    def addon_names(self) -> list[str]:
        if hasattr(self, "addons"):
            return [addon.name for addon in getattr(self, "addons")]
        else:
            return []

    def addon(self, addon: str) -> str:
        if addon in self.addon_names:
            return f"@{self.__class__.__name__.lower()}/{addon}"
        else:
            raise IndexError(f"{addon} is not a plugin/addon for {self.__class__.__name__.lower()}")

    @cached_property
    def name(self) -> str:
        """Name of the integration."""
        return self.__class__.__name__.lower()

    def installed(self, package: str) -> bool:
        path_pkg_json = Path("package.json")
        if path_pkg_json.exists():
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
            self.logger.Info("package.json was not found")
            self.pkgm.ppm.init()
            return False

    def install(self):
        if self.link != "":
            self.logger.Custom(
                "Find out more on the package ",
                url(url=self.link, title=self.name),
                label="Link",
            )

        if not self.installed(self.name):
            self.pkgm.ppm.install(self.name, "-D")

        self.setup()

        if self.has_addons:
            self.require_addons()

    def setup(self):
        """Setup any additional requirements for this package."""
        pass

    def require_addons(self):
        """Ask user if they would like certain addons. Then install them and set them up."""
        pass


class Addon:
    def __init__(self, name: str, desc: str, link: str):
        self.name = name
        self.desc = desc
        self.link = link

    def url(self) -> str:
        """Formatted ansi link to the package link."""
        return url(url=self.link, title=self.name)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{url(url=self.link, title=self.name)} - {self.desc}"


class Sass(Integration):
    def __init__(self, logger: Log, pkgm: PPM):
        super().__init__(logger, pkgm)
        self.link = "https://sass-lang.com/"

    def setup(self):
        """Setup any additional requirements for this package."""
        self.logger.Debug("Adding sass scripts to package.json")
        self.logger.Debug(f"Added\n{snippets['sass_scripts']}")
        with open("./package.json", "r", encoding="utf-8") as package_json:
            from json import load, dumps

            pj = load(package_json)
            if "scripts" not in pj:
                pj["scripts"] = {}
            pj["scripts"].update(snippets["sass_scripts"])

        with open("./package.json", "w", encoding="utf-8") as package_json:
            package_json.write(dumps(pj, indent=2))


class Tailwindcss(Integration):
    def __init__(self, logger: Log, pkgm: PPM):
        super().__init__(logger, pkgm)
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

    def add_tailwind_scripts(self):
        with open("./package.json", "r", encoding="utf-8") as package_json:
            from json import load, dumps

            pj = load(package_json)
            if "scripts" not in pj:
                pj["scripts"] = {}

            pj["scripts"].update(snippets["tailwind_scripts"])

        with open("./package.json", "w", encoding="utf-8") as package_json:
            package_json.write(dumps(pj, indent=2))

    def add_tailwind_css(self):
        Path("styles").mkdir(parents=True, exist_ok=True)
        with open("styles/tailwind.css", "+w", encoding="utf-8") as tailwindcss:
            tailwindcss.write(snippets["tailwind_css"])

    def add_tailwind_config_open(self):
        with open("tailwind.config.js", "+w", encoding="utf-8") as tcss_cfg:
            tcss_cfg.write(snippets["tailwind_config_open"])

    def add_tailwind_config_close(self):
        with open("tailwind.config.js", "a", encoding="utf-8") as tcss_cfg:
            tcss_cfg.write(snippets["tailwind_config_close"])

    def add_tailwind_config_plugin(self, addon: Addon):
        with open("tailwind.config.js", "a", encoding="utf-8") as tcss_cfg:
            tcss_cfg.write(f'    require("@tailwindcss/{addon.name}"),\n')

    def update_refresh_delay(self):
        if Path("moph.json").exists():
            with open("moph.json", "r", encoding="utf-8") as moph_config:
                cfg = load(moph_config)

            if "build" not in cfg:
                cfg["build"] = {}

            cfg["build"]["refresh_delay"] = 3

            with open("moph.json", "w", encoding="utf-8") as moph_config:
                from json import dumps

                moph_config.write(dumps(cfg, indent=2))

    def setup(self):
        """Setup any additional requirements for this package."""
        self.add_tailwind_scripts()
        self.add_tailwind_css()
        self.update_refresh_delay()
        self.add_tailwind_config_open()

    def require_addons(self):
        """Ask user if they would like certain addons. Then install them and set them up."""
        for addon in self.addons:
            install = input(
                color(
                    f"Would you like to install the @tailwindcss/{addon.url()} plugin? [y/N] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
            )
            if install.lower() == "y":
                install = True
            else:
                install = False

            if install:
                if not self.installed(f"@tailwindcss/{addon.name}"):
                    self.pkgm.ppm.install(f"@tailwindcss/{addon.name}", "-D")
                    self.add_tailwind_config_plugin(addon)

        self.add_tailwind_config_close()
