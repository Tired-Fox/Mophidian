from __future__ import annotations
from functools import cached_property

from pathlib import Path
from shutil import copyfile, SameFileError
from typing import Any
import frontmatter

from phml import (
    AST,
    PHML,
    parse_component, substitute_component,
    query,
    replace_node,
    query_all,
    remove_nodes,
    tokanize_name
)
from phml.core import VirtualPython
from phml.builder import p

from markdown import Markdown as MarkdownParse

from config import CONFIG
from .util import REGEX, PAGE_IGNORE, get_group_name, first, html, title

class Node:
    """Base file system node."""

    root: str
    """Root directory of the path."""

    path: str
    """Full path after the root directory."""

    def __init__(self, path: str) -> None:
        splitter = [node for node in path.replace("\\", "/").split("/", 1) if node != ""]
        self.root, self.path = "", ""
        if len(splitter) > 0:
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

    _url: str
    """Relative url from website root. Does not include website root."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.unique = False

        # file name
        file_info = REGEX["file"]["name"].search(path)
        file_name, inherits, inherit_from, extension = (
            file_info.groups() if file_info is not None else ("", None, None, "")
        )

        self.extension = extension or ""
        self.inherit_from = inherit_from or ""
        self.file_name = file_name or ""
        self.inherits = inherits is not None

        # Dest path
        self._dest = self.path
        self.build_dest()

    def build_dest(self):
        while True:
            # Remove group directories from path
            if REGEX["group"]["path"]["middle"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["middle"].sub("/", self._dest)
            elif REGEX["group"]["path"]["start"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["start"].sub("", self._dest)
            else:
                break

        # Replace the file name with index.html
        if self.file_name not in PAGE_IGNORE:
            self._dest = Path("/".join(self._dest.split("/")[:-1])).joinpath("index.html").as_posix()
        else:
            self._dest = Path(self._dest).with_name(self.file_name + ".html").as_posix()
            self.unique = True

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

    next: Renderable | None
    """The next page."""

    prev: Renderable | None
    """The previous page."""

    title: str
    """Title of the page based on the file name."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.layout = None
        self.title = self._make_title()
        self.next = None
        self.prev = None

        # Page url
        if not self.unique:
            self._url = Path(self._dest).parent.as_posix() + "/"
        else:
            self._url = Path(self._dest).as_posix()

        if self._url != "./":
            self._url = "/" + self._url
        else:
            self._url = "/"

    @cached_property
    def url(self) -> str:
        """Url of the page with the website root."""
        url = Path(CONFIG.site.root).joinpath(self._url.lstrip("/")).as_posix()

        if url != ".":
            if self.unique:
                url = "/" + url
            else:
                url = "/" + url + "/"
        else:
            url = "/"
        return url

    def _make_title(self) -> str:
        name = Path(self._dest).parent.as_posix().split("/")[-1]
        if name.strip() in ["", "."]:
            name = self.file_name

        if name == "page":
            name = "home"

        return title(tokanize_name(name))

    def render(self, phml: PHML, **kwargs) -> str:
        """Render the given file to it's appropriate html."""
        raise Exception("Do not use base class Renderable's render function")
    
    def __repr__(self) -> str:
        next = self.next._url if self.next is not None else "None"
        prev = self.prev._url if self.prev is not None else "None"
        return f"{self.__class__.__name__}(path={self.path!r}, url={self._url!r}, prev={prev!r}, next={next!r})"

class TOC:
    """Contains a list of links. Each anchor has a level representing the header level."""

    def __init__(self) -> None:
        self._children = []
    
    @property
    def links(self) -> list[Anchor]:
        """All the anchor links as a flat list."""
        return self._children
    
    def __iter__(self):
        for anchor in self._children:
            yield anchor
    
    def append(self, link: Anchor):
        """Add an anchor object to the toc."""
        self._children.append(link)
        
    def extend(self, links: list[Anchor]):
        """Extend the anchors in the toc."""
        self._children.extend(links)
        
    def remove(self, link: Anchor):
        """Remove a specific anchor from the toc."""
        self._children.remove(link)
        
    def __repr__(self) -> str:
        return f"[{', '.join([repr(child) for child in self._children])}]"

class Anchor:
    """Link representation of a header tag."""

    def __init__(self, name: str, link: str, level: int) -> None:
        self._name = name
        self._level = level
        self._id = link.strip().lstrip("#")

    @cached_property
    def link(self) -> str:
        """Link/href of the anchor."""
        return "#" + self._id

    @property
    def name(self) -> str:
        """Name of the anchor."""
        return self._name

    @property
    def level(self) -> int:
        """Anchor/header level."""
        return self._level
    
    def __eq__(self, __o: object) -> bool:
        return bool(
            isinstance(__o, self.__class__) 
            and self.name == __o.name 
            and self.link == __o.link 
            and self.level == __o.level
        )

    def __repr__(self) -> str:
        return f"{self.name}({self.link!r}, {self.level})"

class Markdown(Renderable):
    """Markdown file representation. These files are rendered with the markdown module
    with the plugins from the config.
    """

    locals: dict[str, Any]
    """Local values from the markdown meta data. Used in rendering the file."""
    
    toc: TOC
    """Table of contents for the markdown page."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.locals = {}
        self.toc = TOC()

    def build_dest(self):
        while True:
            # Remove group directories from path
            if REGEX["group"]["path"]["middle"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["middle"].sub("/", self._dest)
            elif REGEX["group"]["path"]["start"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["start"].sub("", self._dest)
            else:
                break

        if "readme" in Path(self._dest).name.lower():
            # Replace the file name with index.html
            self._dest = (
                Path("/".join(self._dest.split("/")[:-1]))
                    .joinpath("index.html")
                    .as_posix()
            )
        else:
            # Add file name as a directory and make the file index.html in that dir
            self._dest = Path(self._dest).parent.joinpath(self.file_name, "index.html").as_posix()
            
    def parse_toc(self, toc: list):
        """Parse the toc structure from the markdown parser and construct a toc object."""
        result = TOC()
        
        def flat_chilren(children: list):
            for child in children:
                result.append(Anchor(child["name"], child["id"], child["level"]))
                if "children" in child and len(child["children"]) > 0:
                    flat_chilren(child["children"])

        for link in toc:
            result.append(Anchor(link["name"], link["id"], link["level"]))
            if "children" in link and len(link["children"]) > 0:
                flat_chilren(link["children"])

        self.toc = result

    @property
    def ast(self) -> AST:

        # rip meta data from markdown file
        with open(Path(self.root).joinpath(self.path), "r") as markdown_file:
            meta, content = frontmatter.parse(markdown_file.read())

        # convert markdown content to html content
        md = MarkdownParse(
            extensions=CONFIG.markdown.extensions,
            extension_configs=CONFIG.markdown.extension_configs,
        )

        # save meta data as locals for later
        self.locals = meta or {}
        content = md.reset().convert(content)

        self.parse_toc(getattr(md, 'toc_tokens', []))

        # parse resulting html into phml parser
        ast = PHML().parse(content).ast

        # Get the attributes for the wrapper from the config
        klass = " ".join(CONFIG.markdown.wrapper.classes)
        props: dict[str, str] = {}
        if CONFIG.markdown.wrapper.id != "":
            props["id"] = CONFIG.markdown.wrapper.id
        if klass != "":
            props["class"] = klass

        ast.tree = p(None, p(CONFIG.markdown.wrapper.tag, props, *ast.tree.children))
        return ast


    def render(self, phml: PHML, **kwargs):
        """Render the markdown file into a full html page. Apply the plugins
        and configurations from the config. All markdown file meta data is exposed
        to the compiler.

        Args:
            phml (PHML): phml parser/compiler to user.
            **kwargs: Additional variables to expose to the phml compiler.
        """

        ast = phml.parse(html(*CONFIG.site.meta_tags)).ast

        # meta data layout name? then grab layout
        if self.layout is not None:
            page_ast = self.layout.render(self.ast)
        else:
            page_ast = self.ast

        addons = {
            **self.locals,
            "toc": self.toc
        }

        kwargs.update(addons)

        headers = query_all(page_ast, "head")

        remove_nodes(page_ast, {"tag": "head"}, strict=False)

        head_children = []
        for head in headers:
            head_children.extend(head.children)

        head = query(ast, "head")

        if head is not None:
            for header in head_children:
                header.parent = head
                head.children.append(header)
            replace_node(ast.tree, {"tag": "head"}, head)
        replace_node(ast.tree, {"tag": "slot"}, page_ast.children)

        phml.ast = ast
        return phml.render(**kwargs)

class Static(File):
    """Static file representation. These files are not rendered but are still moved to the
    appropriate directory.
    """

    def build_dest(self):
        while True:
            # Remove group directories from path
            if REGEX["group"]["path"]["middle"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["middle"].sub("/", self._dest)
            elif REGEX["group"]["path"]["start"].match(self._dest) is not None:
                self._dest = REGEX["group"]["path"]["start"].sub("", self._dest)
            else:
                break

    @property
    def ast(self) -> AST:
        raise Exception("Static files do not have phml AST's")

    def write(self, dest_dir: str):
        """Write the static file to it's destination directory.

        Args:
            dest_dir: The root dir to place the file into.
        """

        dest = Path(dest_dir).joinpath(self._dest)
        original = Path(self.root).joinpath(self.path)

        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            copyfile(original, dest)
        except SameFileError:
            pass

class Layout(File):
    """Layout representation of a file."""

    parent: Layout | None
    """The parent layout to inherit from."""

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.parent: Layout | None = None

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
                if query(layout_ast, "html") or query(layout_ast, "body"):
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

        if query(page_ast, "html") or query(page_ast, "body"):
            raise Exception("Layout must be components not full pages")
    
        return page_ast

    def render(self, phml: PHML, **kwargs) -> str:
        ast = phml.parse(html(*CONFIG.site.meta_tags)).ast
        if self.layout is not None:
            page_ast = self.layout.render(self.ast)
        else:
            page_ast = self.ast

        headers = query_all(page_ast, "head")

        remove_nodes(page_ast, {"tag": "head"}, strict=False)
        head_children = []
        for head in headers:
            head_children.extend(head.children)

        head = query(ast, "head")
        
        if head is not None:
            for header in head_children:
                header.parent = head
                head.children.append(header)
            replace_node(ast.tree, {"tag": "head"}, head)
        replace_node(ast.tree, {"tag": "slot"}, page_ast.children)

        phml.ast = ast
        return phml.render(**kwargs)

class Nav:
    def __init__(self, name: str) -> None:
        self.children = []
        self.name = name

    def add(self, item: Renderable | Nav):
        """Add a page or sub nav to the current nav object."""
        self.children.append(item)

    def remove(self, item: Renderable | Nav):
        """Remove a page or sub nav from the curren nav object."""
        index = -1
        if isinstance(item, Renderable):
            # TODO: recursive check url with sub navs
            for i, child in enumerate(self.children):
                if isinstance(child, Renderable) and item._url == child._url:
                    index = i
                    break
            error_message = f"Invalid page url {item._url!r}"
        elif isinstance(item, Nav):
            for i, child in enumerate(self.children):
                if isinstance(child, Nav) and item.name == child.name:
                    index = i
                    break
            error_message = f"Invalid nav name {item.name!r}"

        if index == -1:
            raise IndexError(error_message)

        self.children.pop(index)
        
    def print(self, depth: int = 0) -> str:
        """Colored terminal representation of the file."""
        out = (
            f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m \
(\x1b[34m{self.name}\x1b[0m)"
        )
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out
        
    def __str__(self) -> str:
        return self.print()
        
    def __repr__(self) -> str:
        return f"Nav({self.name!r}, children={len(self.children)})"
                

    def __iter__(self):
        """Iterate over the pages and sub navs in order. Starts with pages in alphabetical order
        based on their url's. Next it will iterate over the sub navs in alphabetical order based on
        sub nav name.
        """
        pages = [page for page in self.children if isinstance(page, Renderable)]
        navs = [nav for nav in self.children if isinstance(nav, Nav)]

        pages.sort(key=lambda p: p.url)
        navs.sort(key=lambda n: n.name)

        for page in pages:
            yield page

        for nav in navs:
            yield nav

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
        """Get a layout based on it's file path. This is strict and if no
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
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, path={self.path!r}, children={len(self.children)})"
    
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
            lambda l: sub(r"/?index.html", "", l._dest).strip("/") == path.strip(), pages
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
            elif i != 0:
                if REGEX["group"]["name"].match(segment) is not None:
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
                            if directory.path.strip("/") == '/'.join(path[1:i + 1]):
                                current = directory
                                found = True
                                break

                    # If valid, append a new directory
                    if not found:
                        new = Directory('/'.join(path[: i + 1]) + "/")
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
                for node in [node for node in page._url.split("/") if node != ""]:
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
                if isinstance(page, Page | Markdown)
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

        def recurse_find(current: Container) -> list[File]:
            results = []
            for child in current.children:
                if isinstance(child, File):
                    if compare(child.extension.lstrip(".")):
                        results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))
            return results

        return recurse_find(self)

    def full_paths(self) -> list[str]:
        """Return a list of full paths for every file in the file system."""

        def recurse_find(current: Container) -> list[str]:
            results = []
            for child in current.children:
                if isinstance(child, File):
                    results.append(child.full_path)
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
    
    def static(self) -> list[Static]:
        """List of only static files in the file system."""

        def recurse_find(current: Container) -> list[Static]:
            results = []
            for child in current.children:
                if isinstance(child, Static):
                    results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))
            return results

        return recurse_find(self)

    def renderable(self) -> list[Renderable]:
        """List of only renderable files in the file system."""

        def recurse_find(current: Container) -> list[Renderable]:
            results = []
            for child in current.children:
                if isinstance(child, Renderable):
                    results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))
            return results

        return recurse_find(self)

    def markdown(self) -> list[Markdown]:
        """List of only markdown files in the file system."""

        def recurse_find(current: Container) -> list[Markdown]:
            results = []
            for child in current.children:
                if isinstance(child, Markdown):
                    results.append(child)
                elif isinstance(child, Container):
                    results.extend(recurse_find(child))

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
    
    def __len__(self) -> int:
        return len(self.files())


class Group(Container):
    """Group representation of a Container."""
    def __init__(self, path: str) -> None:
        super().__init__(path, get_group_name([node for node in path.split("/") if node != ""][-1]))


class Directory(Container):
    """Directory representation of a Container."""
    def __init__(self, path: str) -> None:
        path_parts = [node for node in path.split("/") if node != ""]
        name = ""
        if len(path_parts) > 0:
            name = path_parts[-1]
    
        super().__init__(path, name)
