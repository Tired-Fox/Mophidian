"""Builder is a class than combines all core functionality to build a website."""

import contextlib
import os
import shutil
from pathlib import Path
from threading import Thread
from jinja2 import Environment, FileSystemLoader
from mophidian.core.integration import Tailwindcss

from mophidian.core.ppm import PPM
from mophidian.moph_log import Logger, Log

from .config import Config
from .utils import build_template_dict
from .files import get_files
from .navigation import get_navigation
from .navigation import Nav
from .files import Files


class Builder:
    """Builds files into pages. Compiles Sass and Tailwindcss. Static files are also copied to the destination."""

    def __init__(self, logger: Log = Logger):
        self.cfg = Config()
        self.logger = logger
        self.pkg_mgr = PPM(self.cfg.integrations.package_manager, Logger)

    def delete_old(self):
        """If the path to the site already exists delete it."""
        dest = Path(self.cfg.site.dest)
        if dest.exists():
            shutil.rmtree(dest)

    def get_nav(self, files, content) -> Nav:
        """Retrieve the navigation object derived from the page files and content files.

        Args:
            files (Files): Collection of page files
            content (Files): Collection of content files

        Returns:
            Nav: Iterable navigation object.
        """
        return get_navigation(files, content, self.cfg)

    def get_files_and_content(self) -> tuple[Files, Files]:
        """Retrive all page files and content files.

        Returns:
            tuple[Files, Files]: Page files and Content files
        """
        return get_files(self.cfg)

    def copy_all_static_dir(self, dirty: bool = False):
        """If `static/` exists then copy it's contents to the site directory."""
        # Copy all static files from the static/ directory
        static_path = Path("static/")
        if static_path.exists():
            for path in static_path.glob("./**/*.*"):
                dest_path = Path(path.as_posix().replace("static", self.cfg.site.dest))

                if dest_path.exists():
                    if dirty and not os.path.getmtime(path) < os.path.getmtime(dest_path):
                        continue
                    else:
                        shutil.copyfile(path, dest_path)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, dest_path)

    def get_template_tree(self, template_dir: str) -> dict:
        """Retrieve all jinja2.Template's from the given directory.
        These temlates will be exposed to the user and because of that
        they have a special format for accessing them. The path to the file is split
        and nested in a dict to allow the user to use dot notation to access any part
        of the template tree.

        **Example:**

        ```
        layouts
        ├ blog
        │ └ footer.html
        └ header.html
        ```
        Translates to the following as a dictionary
        ```
        {
            'header': <Template>
            'blog': {
                'footer': <Template>
            }
        }
        ```
        The templates can then be accessed with:
        ```html
        {% include lyt.header %}
        {% extend lyt.blog.footer %}
        ```


        Args:
            template_dir (str): Directory to look for templates

        Returns:
            dict: Tree of all the templates which are exposed to the user.
        """
        # Get all jinja2.Template items from directory
        temp = Environment(loader=FileSystemLoader(template_dir))
        return build_template_dict(temp)

    def apply_default_layouts(self, layouts: dict):
        """Append mophidian default layouts to the list of user defined layouts"""

        temp = Environment()

        with open(
            Path(__file__).parent.parent.joinpath("templates/moph_base.html"),
            mode="r",
            encoding="utf-8-sig",
        ) as base_layout:
            layouts["moph_base"] = temp.from_string(base_layout.read())

    def build_pages(
        self,
        nav: Nav,
        components: dict,
        layouts: dict,
        files: Files,
        contents: Files,
        dirty: bool = False,
    ):
        """Iterate through all the pages that are in the
        navigation object and build, render, and write out the pages.

        Args:
            nav (Nav): Navigation object containing all the pages.
            components (dict): Dictionary of all the components
            layouts (dict): Dictionary of all the layouts
        """

        change_count = 0

        for page in nav.pages:
            if dirty and not page.file.is_modified():
                continue
            else:
                page.build_content(self.cfg, layouts)
                change_count += 1

        for page in nav.pages:
            if dirty and not page.file.is_modified():
                continue
            else:
                page.render(self.cfg, components, layouts, nav, files, contents)

                dest = Path(page.file.abs_dest_path)
                dest.parent.mkdir(parents=True, exist_ok=True)

                with open(dest.as_posix(), encoding="utf-8", mode="+w") as page_file:
                    page_file.write(page.content)  # type: ignore

        return change_count

    def build_tailwind(self):
        """Build tailwind styles based on the compiled pages."""

        if self.cfg.integrations.tailwind:
            if self.pkg_mgr.ppm.has_node:
                TAILWIND = Tailwindcss(Logger, self.pkg_mgr)

                with contextlib.redirect_stdout(None):
                    with contextlib.redirect_stderr(None):
                        TAILWIND.install(self.cfg)
                        Path(self.cfg.site.dest).joinpath("css/").mkdir(parents=True, exist_ok=True)
                        self.pkg_mgr.ppm.run("tailwind:mini")

    def rebuild(self, dirty: bool = False):
        """Execute a full site build."""
        if not dirty:
            self.delete_old()

        # Build and retrieve data
        Logger.Info("Finding files")
        files, content = self.get_files_and_content()
        Logger.Info("Constructing page data")
        nav = self.get_nav(files, content)

        # Retrieve components and layouts
        Logger.Info("Retreiving all templates from 'components/' and 'layouts/'")
        components = self.get_template_tree("components/")
        layouts = self.get_template_tree("layouts/")
        self.apply_default_layouts(layouts)

        Logger.Info("Building pages")
        changed = self.build_pages(nav, components, layouts, files, content, dirty=dirty)

        Logger.Success("Pages built")

        self.rebuild_frontend(dirty, changed, files)

        # Copy static files to destination
        Logger.Info("Copying static files")
        self.copy_all_static_dir(dirty)
        files.copy_all_static(dirty)

    def rebuild_frontend(self, dirty: bool, changed: int, files):
        from subprocess import Popen, PIPE
        from shutil import which

        threads = []
        """Current threads that are active."""
        if self.cfg.integrations.sass:
            sass_file = list(
                filter(
                    lambda file: file.is_modified() if dirty else True,
                    [file for file in files if file.is_type(["sass", "scss"])],
                )
            )
            if len(sass_file) > 0:
                self.logger.Custom("sass ...", label="compiling", clr="magenta")
                threads.append(
                    (
                        "sass",
                        Popen(
                            f"{which(self.pkg_mgr.ppm.name())} css:compress",
                            stdout=PIPE,
                            stderr=PIPE,
                        ),
                    )
                )

        if self.cfg.integrations.tailwind and changed > 0:
            self.logger.Custom("tailwind ...", label="compiling", clr="magenta")
            threads.append(
                (
                    "tailwind",
                    Popen(
                        f"{which(self.pkg_mgr.ppm.name())} tailwind:mini", stdout=PIPE, stderr=PIPE
                    ),
                )
            )

        for thread in threads:
            thread[1].wait()
            Logger.Custom(f"{thread[0]}", label="compiled", clr="green")

    def pages(self, dirty: bool = False):
        if not dirty:
            self.delete_old()

        # Build and retrieve data
        Logger.Info("Finding files")
        files, content = self.get_files_and_content()
        Logger.Info("Constructing page data")
        nav = self.get_nav(files, content)

        # Retrieve components and layouts
        Logger.Info("Retreiving all templates from 'components/' and 'layouts/'")
        components = self.get_template_tree("components/")
        layouts = self.get_template_tree("layouts/")
        self.apply_default_layouts(layouts)

        Logger.Info("Building pages")
        change_count = self.build_pages(nav, components, layouts, files, content, dirty=False)

        # Build and apply integrations
        Logger.Info(f"Building all sass files in {self.cfg.site.source}")
        files.build_all_sass(self.cfg, dirty)

        # Build tailwind css
        if change_count > 0:
            self.build_tailwind()

        # Copy static files to destination
        Logger.Info("Copying static files")
        self.copy_all_static_dir(dirty)
        files.copy_all_static(dirty)

        Logger.Success("Site built")

    def full(self, dirty: bool = False):
        """Execute a full site build."""
        if not dirty:
            self.delete_old()

        # Build and retrieve data
        Logger.Info("Finding files")
        files, content = self.get_files_and_content()
        Logger.Info("Constructing page data")
        nav = self.get_nav(files, content)

        # Retrieve components and layouts
        Logger.Info("Retreiving all templates from 'components/' and 'layouts/'")
        components = self.get_template_tree("components/")
        layouts = self.get_template_tree("layouts/")
        self.apply_default_layouts(layouts)

        Logger.Info("Building pages")
        change_count = self.build_pages(nav, components, layouts, files, content, dirty=dirty)

        # Build and apply integrations
        Logger.Info(f"Building all sass files in {self.cfg.site.source}")
        files.build_all_sass(self.cfg, self.pkg_mgr, dirty)

        # Build tailwind css
        if change_count > 0:
            self.build_tailwind()

        # Copy static files to destination
        Logger.Info("Copying static files")
        self.copy_all_static_dir(dirty)
        files.copy_all_static(dirty)

        Logger.Success("Site built")
