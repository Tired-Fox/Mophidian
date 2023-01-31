from __future__ import annotations
from pathlib import Path
from typing import Callable, Iterator

from .util import REGEX
from .base import Node
from .files import File, Layout, Page, Markdown, Static, Renderable, Nav

__all__ = [
    "Container",
    "Group",
    "Directory"
]

def get_group_name(group: str) -> str:
    """Get the group name from the format `(name)`."""
    name = REGEX["group"]["name"].match(group)
    if name is not None:
        return name.group(1)
    return ""

def first(condition: Callable, collection: list | dict | tuple) -> Any:
    """Find the first match given the condition.

    Return:
        Any | None: The found value or None if no value was found.
    """
    if isinstance(collection, dict):
        for value in collection.values():
            if condition(value):
                return value
    else:
        for value in collection:
            if condition(value):
                return value
    return None

class Container(Node):
    """Directory/Group representation of a file system node."""

    name: str
    """Name of the directory/group."""

    children: list
    """Children of the directory/group."""

    def __init__(self, path: str, name: str, ignore: str = "") -> None:
        super().__init__(path, ignore)
        self.children = []
        self.name = name

    def remove(self, full_path: str):
        """Remove a specific file in file system given the files full path.

        Args:
            full_path (str): The full path of the file to remove from the file system.

        Raises:
            Exception: When no file is found that matches the full path.
        """
        def iterate_children(container: Container) -> bool:
            for child in container.children:
                if isinstance(child, File) and child.full_path == full_path:
                    container.children.remove(child)
                    return True
                elif isinstance(child, Container):
                    result = iterate_children(child)
                    if result and len(child.children) == 0:
                        container.children.remove(child)
                    return result
            return False

        if not iterate_children(self):
            raise Exception(f"No file found for full path {full_path!r}")

    def find(self, path: str) -> File | None:
        """Get a file based on it's full source path, path with root stripped, and relative url.
        First the full path is checked, then the path, then the relative url.

        Args:
            path (str): The path to the file.

        Returns:
            File | None: None if no file is found.
        """

        path = path.strip().strip("/")
        
        result = None
        for file in self:
            if file.full_path.strip("/") == path:
                return file
            elif file.path.strip("/") == path:
                return file
            elif file.relative_url.strip("/") == path:
                return file

        return result
    
    def static_by_name(self, name: str) -> File | None:
        """Get a file based on name. Returns the first matching static file.

        Args:
            name (str): The file name or file name partial.

        Returns:
            Page | None: None if no Page is found.
        """

        static_files = self.static()
        
        best_match = None
        for file in static_files:
            if file.file_name == name:
                return file
            elif name in file.file_name:
                best_match = file

        return best_match

    def find_layout_by_path(self, path: list[str]) -> Layout | None:
        """Get a layout based on it's file path. This is strict and if no
        layout is found in the given directory no layout will be used.

        Args:
            path (list): The path split into directories.

        Returns:
            Layout | None: None if no layout is found.
        """

        current = self
        result = first(lambda l: isinstance(l, Layout), current.children)
        for node in path:
            for child in current.children:
                if isinstance(child, Container) and child.name == node:
                    current = child
                    result = first(lambda l: isinstance(l, Layout), current.children) or result
                    break

        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, path={self.path!r}, children={len(self.children)})"

    def __str__(self) -> str:
        out = f"\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.name!r}\x1b[0m"
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(4)
        return out

    def find_page_by_path(self, path: str) -> Layout | None:
        """Get a page based on it's destination path.

        Args:
            path (str): The dest path to the page without the file name.

        Returns:
            Page | None: None if no Page is found.
        """
        from re import sub

        path = path.strip("/")
        pages = self.pages()

        result = first(
            lambda l: sub(r"/?index.html", "", l._dest).strip("/") == path.strip(), list(pages)
        )

        if result is not None:
            return result

        return None

    def find_layout_by_name(self, name: str) -> Layout | None:
        """Name of the layout, either by layout name or group name.

        Example:
            layout name: layout@account.phml
            group name: (account)/layout.phml

        Args:
            name (str): Name of the layout to find. Either name of the layout or the group name
                where the layout is located.

        Returns:
            Layout | None: A layout if found otherwise None.
        """
        if name == "":
            result = first(lambda l: isinstance(l, Layout), self.children)

            if result is not None:
                return result
        else:
            for child in self.children:
                if isinstance(child, Container) and child.name == name:
                    result = first(lambda l: isinstance(l, Layout), child.children)

                    if result is not None:
                        return result
                    break
        return None

    def add(self, item: File | Container):
        """Add a file or directory to the current directory.

        Args:
            item (File | Container): The item to add to the directory
        """
        current = self
        path = [item.root, *[i for i in item.path.split("/") if i.strip() != ""]]
        for i, segment in enumerate(path):
            if Path('/'.join(path[: i + 1])).is_file():
                if len([
                    c for c in current.children
                    if isinstance(c, File)
                    and c.full_path == item.full_path
                ]) > 0:
                    raise Exception(f"Duplicate file at path {item.full_path!r}")
                current.children.append(item)
            elif '/'.join(path[: i + 1]) != item.root:
                new_path = Path(item.root).joinpath(*path[1: i + 1])
                if REGEX["group"]["name"].match(segment) is not None:
                    found = False
                    if current.path.strip("/") == new_path.as_posix():
                        found = True
                    else:
                        for group in [
                            child for child in current.children if isinstance(child, Group)
                        ]:
                            if group.path == '/'.join(path[1 : i + 1]) + "/":
                                current = group
                                found = True
                                break

                    # If valid, append a new group
                    if not found:
                        new = Group(new_path.as_posix(), item.root)
                        current.children.append(new)
                        current = new
                else:
                    found = False

                    if current.path.strip("/") == new_path:
                        found = True
                    else:
                        for directory in [
                            child for child in current.children if isinstance(child, Directory)
                        ]:
                            if directory.path.strip("/") == '/'.join(path[1 : i + 1]):
                                current = directory
                                found = True
                                break

                    # If valid, append a new directory
                    if not found:
                        new = Directory(new_path.as_posix(), item.root)
                        current.children.append(new)
                        current = new
        return current

    def build_nav(self) -> Nav:
        nav = Nav("home")
        nav_indexes = {"nav_pages": []}

        pages = self.renderable()
        for page in pages:
            if not page.unique:
                current = nav_indexes
                for node in [node for node in page.relative_url.split("/") if node != ""]:
                    if REGEX["file"]["name"].match(node) is not None:
                        break
                    else:
                        if node not in current:
                            current[node] = {"nav_pages": []}
                        current = current[node]
                current["nav_pages"].append(page)

        def unwrap_indecies(current: Nav, indecies: dict):
            for page in indecies["nav_pages"]:
                current.add(page)

            for key in indecies:
                if key != "nav_pages":
                    sub_nav = Nav(key)
                    current.add(sub_nav)
                    unwrap_indecies(sub_nav, indecies[key])

        unwrap_indecies(nav, nav_indexes)
        return nav

    def build_hierarchy(self):
        """Build the relationships between layouts and pages."""

        def iterate_layouts(current: Container, parent: Layout | None = None):
            # Layouts without named inheritance
            _layouts = [
                layout
                for layout in current.children
                if isinstance(layout, Layout) and not layout.inherits
            ]

            # Layouts with named inheritance
            _ilayouts = [
                layout
                for layout in current.children
                if isinstance(layout, Layout) and layout.inherits
            ]

            # Directories and Groups
            _containers = [cont for cont in current.children if isinstance(cont, Container)]

            if len(_layouts) > 1:
                raise Exception(f"More than one layout for directory or group: {current.path}")

            # If layout is in current directory assign as current parent layout
            _layout = parent
            if len(_layouts) == 1:
                _layout = _layouts[0]
                _layout.parent = parent

            # Recursively process containers
            for container in _containers:
                iterate_layouts(container, _layout)

            # For all named layouts find it's associated layout
            for lyt in _ilayouts:
                if lyt.inherits:
                    lyt.parent = self.find_layout_by_name(lyt.inherit_from)

        def iterate_pages(current: Container):
            # Renderable files in the current directory
            _pages = [page for page in current.children if isinstance(page, Renderable)]

            # Directories and Groups
            _containers = [cont for cont in current.children if isinstance(cont, Container)]

            for page in _pages:
                if page.inherits:
                    page.layout = self.find_layout_by_name(page.inherit_from)
                else:
                    page.layout = self.find_layout_by_path(page.parents)

            # Recursively process containers
            for container in _containers:
                iterate_pages(container)

        iterate_layouts(self)
        iterate_pages(self)
                

    def files(self, ext: str | list[str] | None = None) -> list[File]:
        """List of all files in file system.

        Example:
            directory.files('css')
            directory.files(['css', 'js'])
            directory.files()

        Args:
            ext (str | list[str] | None): The extension of the files to find.
        """

        def build_compare():
            if ext is None:
                return lambda e: True

            if isinstance(ext, list):
                return lambda e: e in ext
            return lambda e: e == ext

        compare = build_compare()

        return [file for file in self if compare(file.extension.lstrip("."))]

    def full_paths(self) -> list[str]:
        """Return a list of full paths for every file in the file system."""
        return [file.full_path for file in self]

    def pages(self) -> Iterator[Page]:
        """Iterator of only pages in the file system."""
        for file in self:
            if isinstance(file, Page):
                yield file

    def layouts(self) -> Iterator[Layout]:
        """Iterator of only layouts in the file system."""
        for file in self:
            if isinstance(file, Layout):
                yield file

    def static(self) -> Iterator[Static]:
        """Iterator of only static files in the file system."""
        for file in self:
            if isinstance(file, Static):
                yield file

    def renderable(self) -> Iterator[Renderable]:
        """Iterator of only renderable files in the file system."""
        for file in self:
            if isinstance(file, Renderable):
                yield file

    def markdown(self) -> Iterator[Markdown]:
        """Iterator of only markdown files in the file system."""
        for file in self:
            if isinstance(file, Markdown):
                yield file

    def print(self, depth: int = 0) -> str:
        """Colored terminal representation of the container."""
        out = (
            f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.name!r}\x1b[0m"
        )
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out

    def __len__(self) -> int:
        return len(list(self))
    
    def __iter__(self):
        def iterate_children(container: Container):
            for child in container.children:
                if isinstance(child, File):
                    yield child
                else:
                    yield from iterate_children(child)
            
        yield from iterate_children(self)


class Group(Container):
    """Group representation of a Container."""

    def __init__(self, path: str, ignore: str = "") -> None:
        super().__init__(
            path, 
            get_group_name([node for node in path.split("/") if node != ""][-1]), 
            ignore
        )


class Directory(Container):
    """Directory representation of a Container."""

    def __init__(self, path: str, ignore: str = "") -> None:
        path_parts = [node for node in path.split("/") if node != ""]
        name = ""
        if len(path_parts) > 0:
            name = path_parts[-1]

        super().__init__(path, name, ignore)
