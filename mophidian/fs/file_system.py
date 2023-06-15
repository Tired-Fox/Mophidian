from __future__ import annotations
from collections.abc import Callable, Iterator
from functools import cache
from operator import itemgetter
import os
from re import match, sub
from pathlib import Path
from typing import Any, Literal

from watchserver.util import cached_property

from mophidian.config import CONFIG

from .core import FileState, FileType
from .exceptions import PathError


# The goal is to create a dynamic and idiomatic file system data structure.
#
# - [x]  Filterable
# - [x]  Searchable
# - [ ]  Link between files for events
# - [ ]  Hashable
# - [ ]  Printable


def layouts(file: File) -> list[File]:
    lyts = []
    parent = file.parent
    while parent is not None:
        if parent.layout is not None:
            lyts.append(parent.layout)
        parent = parent.parent
    lyts.reverse()
    return lyts


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").replace("//", "/").strip("/")


def _push_fs(parent: Directory, new: File | Directory):
    for i in range(0, len(parent.children)):
        if isinstance(parent.children[i], File):
            if isinstance(new, Directory) or parent.children[i].name > new.name:
                parent.children.insert(i, new)
                return i
        elif isinstance(parent.children[i], Directory):
            if (
                isinstance(new, Directory)
                and parent.children[i].is_group
                and not new.is_group
            ):
                parent.children.insert(i, new)
                return i
            if isinstance(new, Directory) and new.name < parent.children[i].name:
                parent.children.insert(i, new)
                return i
            if (
                isinstance(new, Directory)
                and new.is_group
                and parent.children[i].is_group
                and new.name > parent.children[i].name
            ):
                parent.children.insert(i, new)
                return i
    parent.children.append(new)
    return len(parent.children) - 1


def _compare_fs(fs: FileType, obj: File | Directory) -> bool:
    match fs:
        case FileType.Directory:
            return isinstance(obj, Directory)
        case FileType.Group:
            if not isinstance(obj, Directory):
                return False
            return obj.is_group
        case FileType.File:
            return isinstance(obj, File)
        case FileType.Markdown:
            if not isinstance(obj, File):
                return False
            return obj._ext_ in ["md", "mdx"]
        case FileType.Page:
            if not isinstance(obj, File):
                return False
            return obj._ext_ == "phml" and obj.name.startswith("page")
        case FileType.Layout:
            if not isinstance(obj, File):
                return False
            return obj._ext_ == "phml" and obj.name.startswith("layout")
        case FileType.Static:
            if not isinstance(obj, File):
                return False
            return obj._ext_ != "phml"
        case FileType.All:
            return True
        case _:
            raise Exception("Unkown FileSystem Type")


class FileSystem:
    def __init__(self, path: str) -> None:
        self.root = Directory(path, path)
        self.linked = set()

    def link(self, file: File):
        self.linked.add(file)

    def unlink(self, file: File) -> bool:
        try:
            self.linked.remove(file)
            return True
        except IndexError:
            return False

    def update(self):
        for link in self.linked:
            link.event()

    def by_context(self, key: str, value: Any) -> File | None:
        for file in self.walk(FileType.File):
            if key in file.context and file.context[key] == value:
                return file
        return None

    def clean(self):
        for child in self.walk(FileType.File):
            if child.state == FileState.Deleted:
                os.remove(child._path_)
                child.parent.children.remove(child)

    def search(self, url: str) -> File | Directory | None:
        is_dir = url.endswith("/")

        parts = [part for part in normalize_path(url).split("/") if part != ""]

        current = self
        for file in current.iter():
            if file.url().lstrip("/") == url and _compare_fs(
                FileType.File if not is_dir else FileType.Directory, file
            ):
                return file
        if len(parts) > 0:
            for part in parts:
                dirs: dict = {dir.name: dir for dir in current.iter(FileType.Directory)}
                if part not in dirs:
                    return None
                current = dirs[part]
                for file in current.iter(FileType.File):
                    if file.url().lstrip("/") == url:
                        return file

        if is_dir:
            return current
        else:
            markdown = [
                child
                for child in current.iter(FileType.Markdown)
                if child.name.lower() == "readme"
            ]
            page = [child for child in current.iter(FileType.Page)]
            if len(markdown) >= 1:
                return markdown[0]
            elif len(page) >= 1:
                return page[0]
        return None

    def glob(self, pattern: str) -> FileSystem:
        """Glob system files in current directory and push any files into the file system.

        Uses `Path.glob(<patter>)`

        Return:
            Self for chaining
        """
        for path in self.root._path_.glob(pattern):
            if path.is_file():
                self.push(path.as_posix(), self.root._path_.as_posix())
        return self

    def push(self, path: Path | str, ignore: str = "") -> File | None:
        return self.root.push(path, ignore)

    def get(self, ft: FileType | None = None) -> File | Directory | None:
        """Get the first child. Can optionally filter for a certain file type."""
        self.root.get(ft)

    def last(self, ft: FileType | None = None) -> File | Directory | None:
        """Get the last child. Can optionally filter for a certain file type."""
        self.root.last(ft)

    def iter(self, ft: FileType | None = None) -> Iterator[File | Directory]:
        """Files in the current directory."""
        yield from self.root.iter(ft)

    def walk(self, ft: FileType | None = None) -> Iterator[File | Directory]:
        yield from self.root.walk(ft)

    def files(
        self,
        ft: Literal[
            FileType.File, FileType.Markdown, FileType.Page, FileType.Layout
        ] = FileType.File,
    ) -> Iterator[File]:
        """Iterate the file systems files. Can optionally add additional filters."""
        yield from self.root.walk(ft)

    def walk_dirs(
        self,
        ft: Literal[FileType.Directory, FileType.Group] = FileType.Directory,
    ) -> Iterator[Directory]:
        yield from self.root.walk(ft)

    def __iter__(self):
        yield from self.root.children

    def __getitem__(self, _key_: str) -> File:
        result = self.search(_key_.rstrip("/"))
        if result is None:
            raise KeyError(f"Url not found in file system: {_key_}")
        return result

    def __fstr__(self, indent: int = 0) -> str:
        return self.root.__fstr__(indent)

    def __contains__(self, _key_: str) -> bool:
        return _key_ in self.root

    def __repr__(self) -> str:
        return f"FileSystem(root='{self.root._path_}', children=[{len(self.root.children)}])"


class File:
    __slots__ = (
        "ignore",
        "_path_",
        "_segments_",
        "_ext_",
        "_epoc_",
        "name",
        "label",
        "linked",
        "parent",
        "state",
        "context",
        "title",
    )

    def __init__(
        self, path: str, ignore: str = "", *, parent: Directory | None = None
    ) -> None:
        self._path_: Path = Path(path)
        if not self._path_.is_file():
            raise PathError("Files must exist")

        self.ignore = ignore
        self._segments_: list[str] = self._path_.as_posix().split("/")[:-1]
        self._ext_: str = self._path_.suffix.lstrip(".")

        self.name, self.label = itemgetter("name", "label")(
            match(
                r"(?P<name>[^@]*)(?:@(?P<label>.*))?(?:.phml)?", self._path_.stem
            ).groupdict()
        )

        self.title = self.name
        match self.file_type():
            case FileType.Markdown:
                if self.name == "readme":
                    self.title = Path(self.url()).parent.stem
            case FileType.Page:
                self.title = self._path_.parent.stem.lstrip("(").rstrip(")")

        if self.title.strip() == "":
            self.title = "home"

        self._epoc_: float = self.dest().stat()[8] if self.dest().is_file() else 0
        self.parent: Directory | None = parent
        self.state = FileState.New
        self.linked: set[File] = set()
        self.context: dict[str, Any] = {}

    @property
    def mtime(self) -> float:
        return self._path_.stat()[8] 

    @property
    def path(self) -> str:
        return self._path_.as_posix()

    @cache
    def dest(self) -> Path:
        dest: Path = Path(self.url(CONFIG.paths.out.strip("/")).lstrip("/"))
        match self.file_type():
            case FileType.Markdown:
                dest /= "index.html"
            case FileType.Page:
                dest /= "index.html"
            case _: pass
        return dest

    @cache
    def url(self, base: str | None = None) -> str:
        start = (
            (
                Path(base or CONFIG.site.base)
                .joinpath(sub(f"^/?{self.ignore}/?", "", self._path_.as_posix()))
                .as_posix()
            )
            .lstrip("/")
            .split("/")
        )
        start = "/".join(
            [
                part
                for part in start
                if not part.startswith("(") and not part.endswith(")")
            ]
        )
        match self.file_type():
            case FileType.Markdown:
                if self.name.lower() == "readme":
                    return (
                        "/"
                        + start.rsplit("/", 1)[0].lstrip("/")
                        + "/"
                    ).replace("//", "/")
                else:
                    return (
                        "/" + start.rsplit("/", 1)[0].lstrip("/") + f"/{self.name}/"
                    ).replace("//", "/")
            case FileType.Page:
                if self._path_.stem.startswith("page"):
                    return (
                        "/"
                        + start.rsplit("/", 1)[0].lstrip("/")
                        + "/"
                    ).replace("//", "/")
                else:
                    return (
                        "/"
                        + start.rsplit("/", 1)[0].lstrip("/")
                        + f"/{self.name}/"
                    ).replace('//', '/')
            case _:
                return ("/" + start.lstrip("/")).replace("//", "/")

    def link(self, file: File) -> Callable[[], None]:
        self.linked.add(file)
        return lambda: self.linked.remove(file)

    def event(self):
        self.state = FileState.Force

    def update(self):
        # Remove all linked items that are deleted
        self.linked = set(filter(lambda x: x.state != FileState.Deleted, self.linked))
        for link in self.linked:
            link.event()

    def unlink(self, file: File) -> bool:
        try:
            self.linked.remove(file)
            return True
        except IndexError:
            return False

    @cache
    def file_type(self) -> FileType:
        match self._ext_:
            case "md" | "mdx":
                return FileType.Markdown
            case "phml":
                if self._path_.stem.startswith("layout"):
                    return FileType.Layout
                else:
                    return FileType.Page
        return FileType.Static

    def is_modified(self) -> bool:
        """Check for file modification and update the last modified date.
        The modification is checked between destination file and source file.
        """
        result = self.mtime > self._epoc_ 
        self._epoc_ = self.mtime
        return result

    def get_content(self) -> str:
        """Get the files content."""
        return self._path_.read_text("utf-8")

    def modify(self):
        if self.state != FileState.Deleted:
            self.state = FileState.Modified
            self.update()

    def delete(self):
        self.state = FileState.Deleted

    def updated(self):
        self.state = FileState.NC

    def __fstr__(self, _: int = 0) -> str:
        match self.state:
            case FileState.Modified:
                state = "[\x1b[33m*\x1b[39m] "
            case FileState.New:
                state = "[\x1b[32m+\x1b[39m] "
            case FileState.Deleted:
                state = "[\x1b[31m-\x1b[39m] "
            case _:
                state = ""
        return f"{state}{self._path_.name}"

    def __repr__(self) -> str:
        return f"File(name={self.name!r}, label={self.label!r}, ext={self._ext_!r}, url={self.url()!r})"


class Directory:
    __slots__ = (
        "ignore",
        "_path_",
        "_stem_",
        "name",
        "is_group",
        "layout",
        "children",
        "parent",
    )

    def __init__(
        self, path: str, ignore: str = "", parent: Directory | None = None
    ) -> None:
        self._path_: Path = Path(path)
        self.ignore: str = ignore
        self.parent: Directory | None = parent

        if self._path_.is_file():
            raise PathError("Directory can not be a file")

        self._stem_: str = self._path_.stem
        self.name: str = self._stem_.lstrip("(").rstrip(")")
        self.is_group: bool = self._stem_.startswith("(") and self._stem_.endswith(")")

        self.children: list[Directory | File] = []
        self.layout = None

    @property
    def path(self) -> str:
        return self._path_.as_posix()

    def url(self, base: str = "") -> str:
        return (
            Path(base).joinpath(self._path_.as_posix().lstrip(self.ignore)).as_posix()
        )

    def push(self, path: Path | str, ignore: str = "") -> File | None:
        ignore = ignore if ignore != "" else self.ignore
        path = Path(sub(f"^/?{ignore}/?", "", str(path)))
        segments = path.as_posix().split("/")
        current: Directory = self

        layout = self.layout
        for i, part in enumerate(segments):
            if layout is not None and current.layout is not None:
                layout.link(current.layout)
            layout = current.layout or layout
            if part not in current:
                new_item = Path().joinpath(ignore, *segments[: i + 1])
                if new_item.is_file():
                    new = File(new_item.as_posix(), ignore, parent=current)
                    if new.file_type() == FileType.Layout:
                        if current.layout is not None:
                            raise ValueError(
                                "Can not have multiple layouts in the same directory"
                            )
                        new.linked = set(current.walk(FileType.Page))
                        current.layout = new
                    else:
                        for lyt in layouts(new):
                            lyt.linked.add(new)
                    _push_fs(current, new)
                    return new
                elif new_item.is_dir():
                    i = _push_fs(
                        current, Directory(new_item.as_posix(), ignore, parent=current)
                    )
                    current = current.children[i]
                else:
                    raise PathError(f"Path does not exist: {new_item}")
            else:
                dirs = [dir.name for dir in current.iter(FileType.Directory)]
                current = current.children[dirs.index(part)]

        return None

    def get(self, ft: FileType | None = None) -> File | Directory | None:
        """Get the first child. Can optionally filter for a certain file type."""
        ft = ft or FileType.All
        for child in self:
            if _compare_fs(ft, child):
                return child
        return None

    def last(self, ft: FileType | None = None) -> File | Directory | None:
        """Get the last child. Can optionally filter for a certain file type."""
        ft = ft or FileType.All
        for i in range(len(self.children) - 1, 0, -1):
            if _compare_fs(ft, self.children[i]):
                return self.children[i]
        return None

    def iter(self, ft: FileType | None = None) -> Iterator[File | Directory]:
        """Files in the current directory."""
        ft = ft or FileType.All
        for obj in self.children:
            if _compare_fs(ft, obj):
                yield obj

    def walk(self, ft: FileType | None = None) -> Iterator[File | Directory]:
        ft = ft or FileType.All
        for child in self.children:
            if _compare_fs(ft, child):
                yield child
            if isinstance(child, Directory):
                yield from child.walk(ft)

    def __iter__(self):
        yield from self.children

    def __fstr__(self, indent: int = 0) -> str:
        out = [f"\x1b[35m{self._stem_ or self.name}/\x1b[39m"]
        t = ["└", "├"]
        if len(self.children) == 1:
            t = ["└", "└"]

        for i, child in enumerate(self):
            out.append(
                f"{' ' * indent}{t[0] if i == len(self.children) - 1 else t[1]} {child.__fstr__(indent + 2)}"
            )

        return "\n".join(out)

    def __contains__(self, _key_: str) -> bool:
        for child in self:
            if child.name == _key_:
                return True
        return False

    def __repr__(self) -> str:
        return f"Directory(group={self.is_group}, name={self.name!r}, children=[{len(self.children)}])"
