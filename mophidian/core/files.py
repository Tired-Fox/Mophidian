from __future__ import annotations
import contextlib


import os
from pathlib import Path, PurePath, PurePosixPath
import posixpath
from shutil import SameFileError
import sys
from typing import TYPE_CHECKING, Iterator, Optional, Tuple
from moph_log import Logger, Log, LL
from urllib.parse import quote
from . import utils
from .ppm import PPM
from .integration import Tailwindcss, Sass


if TYPE_CHECKING:
    from .pages import Page
    from .config import Config


class FileExtension:
    Markdown: str = ".md"
    """`.md` | Markdown extension."""
    Template: list[str] = [".html", ".htm"]
    """`.html`, `.htm` | Template extensions."""
    Javascript: str = ".js"
    """`.js` | Javascript extension."""
    CSS: str = ".css"
    """`.css` | CSS extension"""
    SASS: list[str] = [".scss", ".sass"]
    """`.sass`, `.scss` | SASS extensions"""


class Files:
    """A collection of [File][mophidian.core.files.File]"""

    def __init__(self, files: list[File]):
        self._files = files
        self._src_uris: Optional[dict[str, File]]

    def __iter__(self) -> Iterator[File]:
        """Iterate over files."""
        return iter(self._files)

    def __len__(self) -> int:
        """The number of total files."""
        return len(self._files)

    @property
    def src_uris(self) -> dict[str, File]:
        """Dictionary of every file with the key being the files uri."""
        if self._src_uris is None:
            self._src_uris = {file.src_uri: file for file in self._files}
        return self._src_uris

    def get_file(self, path: str) -> Optional[File]:
        """Retrieve a file based on the path."""
        return self.src_uris.get(PurePath(path).as_posix())

    def append(self, file: File):
        """Add file to the collection of files."""
        # Reset the uris so that it can be recalculated
        self._src_uris
        self._files.append(file)

    def remove(self, file: File):
        """Remove file from collection of files."""
        # Reset the uris so that it can be recalculated
        self._src_uris
        self._files.remove(file)

    def copy_all_static(self, dirty: bool = False):
        """Copy all static files to destination."""
        for file in self:
            if file.is_static:
                file.copy_file(dirty)

    def build_all_sass(self, config: Config):
        """Compile all the sass files into their corresponding css files."""

        sass_file = [file for file in self if file.is_type(FileExtension.SASS)]
        print(sass_file)
        if len(sass_file) > 0:
            old_stdo = sys.stdout
            old_stde = sys.stderr

            logger = Log(output=old_stdo, level=LL.INFO)

            if config.integrations.sass:
                pkg_mgr = PPM(config.integrations.package_manager, logger)
                if pkg_mgr.ppm.has_node:
                    SASS = Sass(logger, pkg_mgr, old_stdo, old_stde)

                    with contextlib.redirect_stdout(None):
                        with contextlib.redirect_stderr(None):
                            try:
                                SASS.install(config)
                                Path(config.site.dest_dir).joinpath("css/").mkdir(
                                    parents=True, exist_ok=True
                                )
                                pkg_mgr.ppm.run("css:style:compress")
                                pkg_mgr.ppm.run("css:src:compress")
                            except Exception as e:
                                logger.Error(str(e))

    def template_pages(self, type: FileExtension) -> list[File]:
        """Return list of all template pages."""
        return [file for file in self if file.is_type(FileExtension.Template)]

    def markdwon_pages(self) -> list[File]:
        """Return list of all markdown pages."""
        return [file for file in self if file.is_type(FileExtension.Markdown)]

    def css_pages(self) -> list[File]:
        """Return list of all css pages."""
        return [file for file in self if file.is_type(FileExtension.CSS)]

    def sass_pages(self) -> list[File]:
        """Return list of all sass pages."""
        return [file for file in self if file.is_type(FileExtension.SASS)]

    def javascript_pages(self) -> list[File]:
        """Return list of all javascript pages."""
        return [file for file in self if file.is_type(FileExtension.Javascript)]

    def dir_pages(self, dir: str) -> list[File]:
        """Return all files that have the specified parent directory."""
        return [file for file in self if file.parent == dir]

    def rdir_pages(self, dir: str) -> list[File]:
        """Return all files that contain part of the specified directory."""
        return [file for file in self if dir in file.parent]

    def __getitem__(self, idx: int) -> File:
        return self._files[idx]

    def pretty(self) -> Iterator[str]:
        yield f"Files:"
        for file in self._files:
            yield f"  {repr(file)}"

    def __repr__(self) -> str:
        return "\n".join(self.pretty())


class File:
    """A mophidian File object.

    Stores important file data and points to the appropriate destination based on that data.

    The `path` argument is relative to the `src_dir`

    The `src_dir` and `dest_dir` are the paths from the current working directory (cwd) or absolute paths.

    `directory_url` is a flag on what format the destination paths should follow. True means that each markdown and html file except for index.{md, html} and README.md files get their own directory with their content being represented by a index.html file. Example: `foo.md` = `foo/index.html`. False means the each file is translated to a html file while keeping the same name. Example: `foo.md` = `foo.html`.

    There is additional logic for SASS files and catch all routes. SASS files, `.sass` or `scss` files, with get a destination path with an extension of `.css`. There is also a property that is True if the file is a SASS file. Catch all routes are determined with `[slug].{html, htm}` and recursive catch alls with `[...slug].{html,htm}`. There destination routes are equal to the parent directory as that is where all the corresponding pages should be.

    Mophidian File objects have these properties:
    """

    name: str
    """Name of the file without a suffix/extension."""
    src_uri: str
    """Relative source path to the file, will always use `/` seperation."""
    abs_src_path: str
    """Absolute source path to the file. Uses `\\` on windows."""
    dest_uri: str
    """Relative path to the destination of the file, will always use `/` seperation."""
    abs_dest_path: str
    """Absolute path to the destination of the file. Uses `\\` on windows."""
    parent: str
    """The parent directory of the file."""
    abs_parent: str
    """Absolute parent directory of the file. Uses `\\` on windows."""

    is_index: bool
    """Flag for if the desination file is a index.html file."""

    page: Optional[Page]
    """The page object linked to this file."""

    url: str
    """The uri of the destination file relative to the destination directory"""

    @property
    def src_path(self) -> str:
        """Same path as src_uri except it will use `\\` on windows. Not recommended"""
        return os.path.normpath(self.src_uri)

    @src_path.setter
    def src_path(self, new_value: str | PurePath | Path):
        self.src_uri = PurePath(new_value).as_posix()

    @property
    def dest_path(self) -> str:
        """Same path as dest_uri except it will use `\\` on windows. Not recommended"""
        return os.path.normpath(self.dest_uri)

    @dest_path.setter
    def dest_path(self, new_value: str | PurePath | Path):
        self.dest_uri = PurePath(new_value).as_posix()

    def is_type(self, ext: str | list[str]) -> bool:
        """Check if file is a certain type. Valid types are given by FileExtension or you can provide your own.

        Arguments:
            ext (str | list[str]): FileExtension has predefined file types otherwise you can provide a str or list of strings to use. The string values must be of the format `.ext`.
        """
        if isinstance(ext, str):
            return self._suffix == ext
        elif isinstance(ext, list):
            return self._suffix in ext

    @property
    def is_static(self) -> bool:
        """Flag for if the file is static."""
        return (
            not self.is_type(FileExtension.Template)
            and not self.is_type(FileExtension.Markdown)
            and not self.is_type(FileExtension.SASS)
        )

    @property
    def is_dyn(self) -> bool:
        """Flag for if the file is a dynamic route/file."""
        return self.name == '[slug]' and self.is_type(FileExtension.Template)

    @property
    def is_rdyn(self) -> bool:
        """Flag for if the file is a recursive dynamic route/file."""
        return self.name == '[...slug]' and self.is_type(FileExtension.Template)

    def __init__(self, path: str, src_dir: str, dest_dir: str, directory_url: bool):
        if not src_dir.endswith("/"):
            src_dir += "/"
        if not dest_dir.endswith("/"):
            dest_dir += "/"

        self.src_path = PurePath(path).as_posix().replace(src_dir, "")
        self.parent = PurePath(self.src_path).parent.as_posix()

        self.abs_src_path = os.path.normpath(os.path.join(src_dir, self.src_path))
        self.abs_parent = os.path.normpath(PurePath(self.abs_src_path).parent.as_posix())

        self.name = self._build_stem()
        self._suffix = PurePath(path).suffix

        self.dest_path = self._build_dest_path(directory_url)
        self.is_index = PurePath(self.dest_path).name == "index.html"
        self.abs_dest_path = os.path.normpath(os.path.join(dest_dir, self.dest_path))

        self.url = self._build_url(directory_url)
        self.page = None

    def is_modified(self) -> bool:
        """Check if the file is modified based on the src_path and dest_path."""
        if os.path.isfile(self.abs_dest_path):
            return os.path.getmtime(self.abs_dest_path) < os.path.getmtime(self.abs_src_path)
        return True

    def _build_url(self, directory_url: bool) -> str:
        """Build the url based on the destination path."""
        url = self.dest_uri
        dir, file = posixpath.split(url)
        if directory_url and file == 'index.html':
            if dir == '':
                url = '.'
            else:
                url = "/" + dir + '/'

        return quote(url)

    def _build_dest_path(self, directory_url: bool) -> str:
        """Build the destination path based on the source.

        1. Directory based url or index page
                - index.md, index.html, README.md => index.html
                - foo.md, foo.html => foo/index.html
        2. Catch all routes
                - These routes take files from the `content` directory
                - blog/[slug].html => blog/
                - blog/[...slug].html => blog/
        3. Sass files get integration paths
                - foo.scss or foo.sass => foo.css
        4. Non-directory based url
                - bar.md, bar.html => bar.html

        Args:
            directory_url (bool): Whether to use directory based urls

        Returns:
            str: The transformed/built destination path
        """
        if self.is_type(FileExtension.Markdown) or self.is_type(FileExtension.Template):
            parent = PurePath(self.src_path).parent
            if not directory_url or self.name == 'index':
                # index.md, index.html, README.md => index.html
                # foo.md, foo.html => foo.html
                return posixpath.join(parent, self.name + ".html")
            elif self.name in ['[slug]', '[...slug]']:
                return parent.as_posix()
            else:
                # Directory based routing
                # bar.md or bar.html => bar/index.html
                return posixpath.join(parent, self.name, "index.html")
        elif self.is_type(FileExtension.SASS):
            return PurePath(self.src_path).with_suffix(".css").as_posix()

        # If the file is a static file it is one to one
        return self.src_path

    def _build_stem(self) -> str:
        """Build the stem / filename without extension.

        index, README => index

        Returns:
            str: File stem.
        """
        filename = PurePosixPath(self.src_uri).name
        stem, _ = posixpath.splitext(filename)
        return 'index' if stem in ('index', 'README') else stem

    def prettify(self) -> Iterator[str]:
        """Yields one line at a time of the prettified representation of the file data.

        Yields:
            Iterator[str]: Yields one line at a time.
        """
        yield "File ("
        yield f"  name: {self.name}"
        yield f"  suffix: {self._suffix}"
        yield f"  src_path: {self.src_path}"
        yield f"  abs_src_path: {self.abs_src_path}"
        yield f"  dest_path: {self.dest_path}"
        yield f"  abs_dest_path: {self.abs_dest_path}"
        yield f"  dynamic: {self.is_dyn}"
        yield f"  recursive_dynamic: {self.is_rdyn}"
        yield f")"

    def copy_file(self, dirty: bool = False):
        """Copy file to destination, ensuring parent exists. Mainly for static files."""
        if dirty and not self.is_modified():
            Logger.Info(f"Skipping unmodified file: '{self.src_uri}'")
        else:
            Logger.Info(f"Copying static file: '{self.src_uri}'")
            try:
                utils.copy_file(self.abs_src_path, self.abs_dest_path)
            except SameFileError:
                pass

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.src_uri == other.src_uri
            and self.abs_src_path == other.abs_src_path
            and self.url == other.url
        )

    def __repr__(self) -> str:
        return f"File (name: {self.name}, suffix: {self._suffix}, src_path: {self.src_path}, url: {self.url})"

    def __str__(self) -> str:
        return f"File (name: {self.name}, suffix: {self._suffix}, src_path: {self.src_path}, url: {self.url})"


def get_files(config: Config) -> Tuple[Files, Files]:
    """Glob the `src_dir` and return a Files collection. Also, glob the `content_dir` and return a File collection.

    Returns:
        Tuple[Files, Files]: File collection for both pages an content.
    """
    pages = []
    src_path = Path(config.site.src_dir)
    if src_path.exists():
        for path in src_path.glob(f"./**/*.*"):
            pages.append(
                File(
                    path.as_posix(),
                    config.site.src_dir,
                    config.site.dest_dir,
                    config.nav.directory_url,
                )
            )

    content = []
    content_path = Path(config.site.content_dir)
    if content_path.exists():
        for path in content_path.glob(f"./**/*.*"):
            if path.suffix == ".md":
                content.append(
                    File(
                        path.as_posix(),
                        config.site.content_dir,
                        config.site.dest_dir,
                        directory_url=True,
                    )
                )

    return Files(pages), Files(content)
