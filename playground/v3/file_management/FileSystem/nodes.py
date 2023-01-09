from __future__ import annotations
from pathlib import Path

from phml import AST, PHML, parse_component, substitute_component, query, replace_node
from phml.core import VirtualPython
from .util import REGEX, get_group_name, first, html

class Node:
    """Base file system node."""

    root: str
    """Root directory of the path."""

    path: str
    """Full path after the root directory."""

    def __init__(self, path: str) -> None:
        splitter = [node for node in path.replace("\\", "/").split("/", 1) if node != ""]
        self.root, self.path = splitter if len(splitter) > 1 else (splitter[0], splitter[0])
        self.full_path = path
        self.children = None

    @property
    def parents(self) -> list[str]:
        """Parent directories as a list of strings."""
        return [node for node in Path(self.path).parent.as_posix().split("/") if node != "."]

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self.__class__) and __o.path == self.path

    def __str__(self) -> str:
        out = f"\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.path!r}\x1b[0m"
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(4)
        return out


class File(Node):
    """File representation in the file system."""

    file_name: str
    """Name of the file without it's extension."""

    extension: str
    """Extension of the file."""

    inherits: bool
    """Flag for if the file inherits from a layout."""

    inherit_from: str
    """Name of the layout to inherit from based on group name. Blank, '', name means root layout."""

    def __init__(self, path: str) -> None:
        super().__init__(path)

        # Dest path
        self._dest = self.path
        while True:
            # Remove group directories from path
            if REGEX["group"]["path"]["middle"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["middle"].sub("/", self._dest)
            elif REGEX["group"]["path"]["start"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["start"].sub("", self._dest)
            else:
                break

        # Replace the file name with index.html
        self._dest = Path("/".join(self._dest.split("/")[:-1])).joinpath("index.html").as_posix()

        # file name
        file_info = REGEX["file"]["name"].search(path)
        file_name, inherits, inherit_from, extension = (
            file_info.groups() if file_info is not None else ("", None, None, "")
        )

        self.extension = extension or ""
        self.inherit_from = inherit_from or ""
        self.file_name = file_name or ""
        self.inherits = inherits is not None

        # TODO: url

    @property
    def ast(self) -> AST:
        """Parsed phml ast of the file."""
        raise Exception("Do not use base File class's ast property")
    
    def dest(self, dest_dir: str) -> Path:
        """Destination path of the file given a destination directory."""
        return Path(dest_dir).joinpath(self._dest)

    def print(self, depth: int = 0) -> str:
        """Colored terminal representation of the file."""
        out = (
            f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m > \
\x1b[32m{self.file_name+self.extension!r}\x1b[0m"
        )
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path!r}, inherits={self.inherits!r}, \
inherit_from={self.inherit_from!r})"

class Renderable(File):
    """Renderable file."""

    layout: Layout | None
    """The layout to apply while rendering a file."""

    def __init__(self, path: str) -> None:
        self.layout = None
        super().__init__(path)

    def render(self, phml: PHML) -> str:
        """Render the given file to it's appropriate html."""
        raise Exception("Do not use base class Renderable's render function")

class Layout(File):
    """Layout representation of a file."""

    parent: Layout | None
    """The parent layout to inherit from."""

    def __init__(self, path: str) -> None:
        self.parent: Layout | None = None
        super().__init__(path)

    def __fetch_layouts(self) -> list[Layout]:
        lyts = [self]
        parent = self.parent
        while parent is not None:
            lyts.append(parent)
            parent = parent.parent
        return list(reversed(lyts))

    @property
    def ast(self) -> AST:
        phml = PHML()
        layouts = self.__fetch_layouts()
        ast = phml.parse("<slot/>").ast

        # Start with slot element and replace the slot element with each inherited layout
        for layout in layouts:
            try:
                layout_ast = phml.load(Path(self.root).joinpath(layout.path)).ast

                # If it quacks like a full page, then it's a full page
                if (
                    query(layout_ast, "html") or query(layout_ast, "head")
                    or query(layout_ast, "body")
                ):
                    raise Exception("Layout must be components not full pages")

                component: dict = parse_component(layout_ast)
            except Exception as error:
                raise Exception("Layout must be a valid phml component") from error

            if query(component["component"], "slot") is None:
                raise Exception("Layout must contain a slot element")

            # Replace the slot element in the parent with the next layout
            substitute_component(ast.tree, ("slot", component), VirtualPython())
        return ast

    def render(self, page: AST) -> AST:
        """Render a page given this layouts phml AST.

        Args:
            page: The ast of the page to use.

        Return:
            AST: The combinded phml ast of the layout and the page.

        Note:
            The ast is still not a full html ast at this point.
        """
        ast = self.ast
        try:
            component: dict = parse_component(page)
        except Exception as error:
            raise Exception("Page must be a valid phml component") from error

        substitute_component(ast.tree, ("slot", component), VirtualPython())
        return ast

class Component(File):
    pass

class Page(Renderable):
    """Page representation of a File."""

    @property
    def ast(self) -> AST:
        phml = PHML()
        page_ast = phml.load(Path(self.root).joinpath(self.path)).ast

        if query(page_ast, "html") or query(page_ast, "head") or query(page_ast, "body"):
            raise Exception("Layout must be components not full pages")
        return page_ast

    def render(self, phml: PHML, **kwargs) -> str:
        ast = phml.parse(html).ast
        if self.layout is not None:
            replace_node(ast.tree, {"tag": "slot"}, self.layout.render(self.ast).children)
        else:
            replace_node(ast.tree, {"tag": "slot"}, self.ast.children)

        phml.ast = ast
        return phml.render(**kwargs)


class Container(Node):
    """Directory/Group representation of a file system node."""

    name: str
    """Name of the directory/group."""

    children: list
    """Children of the directory/group."""

    def __init__(self, path: str, name: str) -> None:
        super().__init__(path)
        self.children = []
        self.name = name

    def find_layout_by_path(self, path: list[str]) -> Layout | None:
        """Get the layout based on it's file path. This is strict and if no
        layout is found in the given directory no layout will be used.

        Args:
            path (list): The path split into directories.

        Returns:
            Layout | None: None if no layout is found.
        """

        current = self
        for node in path:
            for child in current.children:
                if isinstance(child, Container) and child.name == node:
                    current = child
                    break

        result = first(
            lambda l: isinstance(l, Layout), current.children
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
            result = first(
                lambda l: isinstance(l, Layout), self.children
            )

            if result is not None:
                return result
        else:
            for child in self.children:
                if isinstance(child, Container) and child.name == name:
                    result = first(
                        lambda l: isinstance(l, Layout), child.children
                    )

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
        path = [item.root, *item.path.split("/")]
        
        for i, segment in enumerate(path):
            if Path('/'.join(path[:i+1])).is_file():
                current.children.append(item)
            elif REGEX["group"]["name"].match(segment) is not None:
                found = False
                if current.path.strip("/") == "/".join(path[:i+1]):
                    found = True
                else:
                    for group in [child for child in current.children if isinstance(child, Group)]:
                        if group.path == '/'.join(path[1 : i + 1]) + "/":
                            current = group
                            found = True
                            break

                # If valid, append a new group
                if not found:
                    new = Group('/'.join(path[: i + 1]) + "/")
                    current.children.append(new)
                    current = new
            else:
                found = False
                
                if current.path.strip("/") == "/".join(path[:i+1]):
                    found = True
                else:
                    for directory in [
                        child for child in current.children if isinstance(child, Directory)
                    ]:
                        if directory.path.strip("/") == '/'.join(path[:i + 1]):
                            current = directory
                            found = True
                            break

                # If valid, append a new directory
                if not found:
                    new = Directory('/'.join(path[: i + 1]) + "/")
                    current.children.append(new)
                    current = new
        return current

    def build_hierarchy(self):
        """Build the relationships between layouts and pages."""

        def iterate_layouts(current: Container, parent: Layout | None = None):
            # Layouts without named inheritance
            _layouts = [
                layout for layout in current.children 
                if isinstance(layout, Layout) and not layout.inherits
            ]

            # Layouts with named inheritance
            _ilayouts = [
                layout for layout in current.children 
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
            # Pages in the current directory
            _pages = [
                page for page in current.children 
                if isinstance(page, Page)
            ]

            # Directories and Groups
            _containers = [cont for cont in current.children if isinstance(cont, Container)]

            for page in _pages:
                if page.inherits:
                    page.layout = self.find_layout_by_name(page.inherit_from)
                else:
                    page.layout = self.find_layout_by_path(page.parents)

            # Recursively process containers
            for container in _containers:
                iterate_layouts(container)

        iterate_layouts(self)
        iterate_pages(self)

    def files(self) -> list[File]:
        """List of all files in file system."""

        def recurse_find(current: Container) -> list[File]:
            results = []
            for child in current.children:
                if isinstance(child, File):
                    results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))
            return results

        return recurse_find(self)

    def pages(self) -> list[Page]:
        """List of only pages in the file system."""

        def recurse_find(current: Container) -> list[Page]:
            results = []
            for child in current.children:
                if isinstance(child, Page):
                    results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))
            return results

        return recurse_find(self)

    def layouts(self) -> list[Layout]:
        """List of only layouts in the file system."""

        def recurse_find(current: Container) -> list[Layout]:
            results = []
            for child in current.children:
                if isinstance(child, Layout):
                    results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))
            return results

        return recurse_find(self)

    def print(self, depth: int = 0) -> str:
        """Colored terminal representation of the container."""
        out = (
            f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.name!r}\x1b[0m"
        )
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out


class Group(Container):
    """Group representation of a Container."""
    def __init__(self, path: str) -> None:
        super().__init__(path, get_group_name([node for node in path.split("/") if node != ""][-1]))


class Directory(Container):
    """Directory representation of a Container."""
    def __init__(self, path: str) -> None:
        super().__init__(path, [node for node in path.split("/") if node != ""][-1])
