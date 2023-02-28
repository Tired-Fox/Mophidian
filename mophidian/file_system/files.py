from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property

from pathlib import Path
from shutil import copyfile, SameFileError # For copying static files
from typing import TYPE_CHECKING, Any
from re import match

import frontmatter # Used to rip the metadata from markdown files
from phml import ( # Used to parse the phml content and manipulate it's ast
    AST,
    check,
    cmpt_name_from_path,
    find,
    PHML,
    parse_component,
    query,
    query_all,
    remove_nodes,
    replace_node,
    substitute_component,
    tokanize_name,
)
from phml.core import VirtualPython # Dummy instance for subtituting elements for <Slot />
from phml.builder import p # To create injected elements
from saimll import SAIML, Logger # Custom logging

from markdown import Markdown as MarkdownParse # For parsing markdown files into html

import mophidian
from mophidian.config import CONFIG
from mophidian.core.util import REGEX, PAGE_IGNORE, html, title, url
from .markdown_extensions import _RelativePathExtension
from .base import apply_attribute_configs, build_attributes, Node

if TYPE_CHECKING:
    from .containers import Directory

__all__ = [
    "File",
    "Renderable",
    "Layout",
    "Static",
    "Page",
    "Markdown",
    "Component",
    "TOC",
    "Anchor",
    "Nav",
    "FileState"
]

@dataclass
class FileState:
    """File's state

    States:
        (0) DEFAULT: Already up to date and doesn't need to be rendered
        (1) UPDATED: New file or file has been modified and needs to be rendered
        (2) DELETE : File no longer exists so delete it
    """
    NULL: int = 0
    UPDATED: int = 1
    DELETED: int = 2
    
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

class Linker:
    """Base class defining logic for linking pages to other objects."""

    linked_files: list[Renderable]
    """List of pages using this class. Includes nested pages deep in linked tree."""
    
    def __init__(self) -> None:
        self.linked_files = []

    def link_file(self, page: Renderable):
        """Add a page to the list of linked page objects. Only add it if it isn't linked."""

        if not self.is_linked(page) and isinstance(page, Renderable):
            self.linked_files.append(page)

    def unlink_file(self, page: Renderable):
        """Remove a page from the list of linked page objects."""

        if self.is_linked(page) and isinstance(page, Renderable):
            self.linked_files.remove(page)

    def is_linked(self, page: Renderable):
        """Check if a page is linked to this object."""
        return page in self.linked_files

    def update_linked(self):
        """Sets all linked pages state to updated."""
        for page in self.linked_files:
            page.state = FileState.UPDATED

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

    relative_url: str
    """Relative url from website root. Does not include website root."""

    state: int
    """State of the file, either needs a update/render, needs to be deleted, or neither."""

    epoch: float
    """Timestamp of when the file was last rendered. Used in live reloading."""

    def __init__(self, path: str, ignore: str = "", unique: bool = False) -> None:
        super().__init__(path, ignore)
        self.unique = unique
        self.epoch = 0.0

        # file name
        file_info = REGEX["file"]["name"].search(path)
        file_name, inherits, inherit_from, extension = (
            file_info.groups() if file_info is not None else ("", None, None, "")
        )

        self.state = FileState.UPDATED
        self.extension = extension or ""
        self.inherit_from = inherit_from or ""
        self.file_name = file_name or ""
        self.inherits = inherits is not None

        # Dest path
        self._dest = self.src
        self.build_dest()

         # Page url
        if not self.unique:
            self.relative_url = Path(self._dest).parent.as_posix() + "/"
        else:
            self.relative_url = Path(self._dest).as_posix()

        if self.relative_url != "./":
            self.relative_url = "/" + self.relative_url.lstrip("/")
        else:
            self.relative_url = "/"

    @cached_property
    def url(self) -> str:
        """Url of the page with the website root."""
        url = Path(CONFIG.site.root).joinpath(self.relative_url.lstrip("/")).as_posix()

        if url != ".":
            if self.unique:
                url = "/" + url
            else:
                url = "/" + url + "/"
        else:
            url = "/"
        return url

    def build_dest(self):
        # Replace the file name with index.html
        if self.file_name not in PAGE_IGNORE:
            self._dest = (
                Path("/".join(self._dest.split("/")[:-1])).joinpath("index.html").as_posix()
            )
        else:
            self._dest = Path(self._dest).with_name(self.file_name + ".html").as_posix()
            self.unique = True

    @property
    def ast(self) -> AST:
        """Parsed phml ast of the file."""
        raise Exception("Do not use base File class's ast property")

    def dest(self, dest_dir: str) -> Path:
        """Destination path of the file given a destination directory."""
        return Path(dest_dir).joinpath(self._dest.strip("/"))

    def print(self, depth: int = 0) -> str:
        """Colored terminal representation of the file."""
        out = f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m > \
\x1b[32m{self.file_name+self.extension!r}\x1b[0m"
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path!r}, url={self.relative_url!r}, inherits={self.inherits!r}, \
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
    
    components: list[Component]
    """List of used components. For live updates only."""

    def __init__(self, path: str, ignore: str = "") -> None:
        super().__init__(path, ignore)
        self.layout = None
        self.components = []
        self.title = self._make_title()
        self.next = None
        self.prev = None
        
    def delete(self):
        layout = self.layout

        while layout is not None:
            layout.unlink_file(self)
            layout = layout.parent

        for component in self.components:
            component.unlink_file(self)

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
        next = self.next.relative_url if self.next is not None else "None"
        prev = self.prev.relative_url if self.prev is not None else "None"
        return f"{self.__class__.__name__}(path={self.path!r}, url={self.relative_url!r}, prev={prev!r}, next={next!r})"

class Page(Renderable):
    """Page representation of a File."""

    @property
    def ast(self) -> AST:
        phml = PHML()
        page_ast = phml.load(Path(self.full_path)).ast

        if query(page_ast, "html") or query(page_ast, "body"):
            Logger.warning(f"<{SAIML.parse(f'[@Fgreen]{self.full_path!r}')}> Page must be a component not full pages")

        return page_ast

    def render(self, phml: PHML, component_files: Directory, **kwargs) -> str:
        # Remove unwanted kwargs
        kwargs.pop("static_files", None)
        kwargs.pop("page_files", None)

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
            for node in head_children:
                node.parent = head
                exist = '[{}]'
                exist_equal = '[{}={}]'
                if check(node, "element") and node.tag in ["meta", "title"]:
                    old_tag = query(
                        head,
                        f"{node.tag}{''.join(exist.format(key) for key in node.properties.keys())}",
                    )
                    if node is not None:
                        replace_node(head, lambda n, i, p: n == old_tag, node)
                    else:
                        head.children.append(node)
                elif check(node, "element") and node.tag not in ["style", "script"]:
                    if (
                        query(
                            head,
                            f"{node.tag}\
{''.join(exist_equal.format(key, value) for key, value in node.properties.items())}",
                        )
                        is None
                    ):
                        head.children.append(node)
                else:
                    # replace or append
                    head.children.append(node)
            replace_node(ast.tree, {"tag": "head"}, head)
        replace_node(ast.tree, {"tag": "Slot"}, page_ast.children)

        # Find all components
        for component in component_files.components():
            if find(ast, {"tag": component.cname}) is not None:
                component.link_file(self)
                self.components.append(component)

        ast = apply_attribute_configs(ast)
        ast = phml.compile(**kwargs)

        if CONFIG.build.rss:
            rss_link = query(ast, "link[type*=rss]")
            if rss_link is not None:
                rss_link.properties.update({
                    "type": "application/rss+xml",
                    "rel": "alternate",
                    "href": Path(CONFIG.site.base_url).joinpath(CONFIG.site.root, "feed.xml")
                })

        # Fix href and src links
        root = "/" + CONFIG.site.root.strip("/")
        for link_type in ["href", "src", "xlink:href"]:
            for node in query_all(ast, f"[{link_type}^=/]"):
                if not node[link_type].startswith(root):
                    node[link_type] = root + node[link_type]

        phml.ast = ast

        return phml.render(**kwargs)

class Markdown(Renderable):
    """Markdown file representation. These files are rendered with the markdown module
    with the plugins from the config.
    """

    locals: dict[str, Any]
    """Local values from the markdown meta data. Used in rendering the file."""

    toc: TOC
    """Table of contents for the markdown page."""

    def __init__(self, path: str, ignore: str = "") -> None:
        super().__init__(path, ignore)
        self.locals = {}
        self.toc = TOC()
        self.relative_path_extension = None

    def build_dest(self):
        if "readme" in Path(self._dest).name.lower():
            # Replace the file name with index.html
            self._dest = (
                Path("/".join(self._dest.split("/")[:-1])).joinpath("index.html").as_posix()
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

    def _make_title(self) -> str:

        with open(self.full_path, "r", encoding="utf-8") as mfile:
            for line in mfile.readlines():
                if line.strip() != "":
                    header_1 = match(r"\s*# ?(.+)", line)
                    if header_1 is not None:
                        return header_1.group(1).strip()

        name = Path(self._dest).parent.as_posix().split("/")[-1]
        if name.strip() in ["", "."]:
            name = self.file_name

        if name == "page":
            name = "home"

        return title(tokanize_name(name))

    @property
    def ast(self) -> AST:

        # rip meta data from markdown file
        with open(Path(self.full_path), "r", encoding="utf-8") as markdown_file:
            meta, content = frontmatter.parse(markdown_file.read())

        # convert markdown content to html content
        try:
            if self.relative_path_extension is None:
                extensions = CONFIG.markdown.extensions
            else:
                extensions = [self.relative_path_extension, *CONFIG.markdown.extensions]
            md = MarkdownParse(
                extensions=extensions,
                extension_configs=CONFIG.markdown.extension_configs,
            )
        except KeyError as key_error:
            from traceback import print_exc

            print_exc()
            SAIML.print(
                f"*[@Fred]KeyError[@F]:[] invalid variable in extension configs [$@Fgreen]{key_error}"
            )
            exit()

        # save meta data as locals for later
        self.locals = meta or {}
        content = md.reset().convert(content)

        self.parse_toc(getattr(md, 'toc_tokens', []))

        # parse resulting html into phml parser
        ast = PHML().parse(content).ast

        # Get the attributes for the wrapper from the config
        props: dict[str, str] = build_attributes(CONFIG.markdown.wrapper.attributes)

        ast.tree = p(None, p(CONFIG.markdown.wrapper.tag, props, *ast.tree.children))
        return ast

    def render(self, phml: PHML, page_files: Directory, static_files: Directory, component_files: Directory, **kwargs):
        """Render the markdown file into a full html page. Apply the plugins
        and configurations from the config. All markdown file meta data is exposed
        to the compiler.

        Args:
            phml (PHML): phml parser/compiler to user.
            **kwargs: Additional variables to expose to the phml compiler.
        """

        ast = phml.parse(html(*CONFIG.site.meta_tags)).ast

        self.relative_path_extension = _RelativePathExtension(self, page_files, static_files)

        self._make_title()

        # meta data layout name? then grab layout
        if self.layout is not None:
            page_ast = self.layout.render(self.ast)
        else:
            page_ast = self.ast

        addons = {**self.locals, "toc": self.toc, "title": self.locals.get("title", None) or self.title}

        kwargs.update(addons)

        headers = query_all(page_ast, "head")

        remove_nodes(page_ast, {"tag": "head"}, strict=False)

        head_children = []
        for head in headers:
            head_children.extend(head.children)

        head = query(ast, "head")
        if head is not None:
            if CONFIG.markdown.pygmentize.highlight:
                if (
                    page_files.find(CONFIG.markdown.pygmentize.path) is None
                    and static_files.find(CONFIG.markdown.pygmentize.path) is None
                ):
                    if not mophidian.states["markdown_code_highlight_warned"]:
                        Logger.warning(
                            "Markdown code highlighting requires a pygmentize css file. \
Use `moph highlight` to create that file."
                        )
                        mophidian.states["markdown_code_highlight_warned"] = True
                else:
                    head.insert(
                        -1,
                        p(
                            "link",
                            {"rel": "stylesheet", "href": url(CONFIG.markdown.pygmentize.path)},
                        ),
                    )
            for node in head_children:
                node.parent = head
                exist = '[{}]'
                exist_equal = '[{}="{}"]'
                if check(node, "element") and node.tag in ["meta", "title"]:
                    old_tag = query(
                        head,
                        f"{node.tag}{''.join(exist.format(key) for key in node.properties.keys())}",
                    )
                    if node is not None:
                        replace_node(head, lambda n, i, p: n == old_tag, node)
                    else:
                        head.children.append(node)
                elif check(node, "element") and node.tag not in ["style", "script"]:
                    if (
                        query(
                            head,
                            f"{node.tag}\
{''.join(exist_equal.format(key, value) for key, value in node.properties.items())}",
                        )
                        is None
                    ):
                        head.children.append(node)
                else:
                    # replace or append
                    head.children.append(node)
            replace_node(ast.tree, {"tag": "head"}, head)

        replace_node(ast.tree, {"tag": "Slot"}, page_ast.children)

        # Find all components
        for component in component_files.components():
            if find(ast, {"tag": component.cname}) is not None:
                component.link_file(self)
                self.components.append(component)

        ast = apply_attribute_configs(ast)
        ast = phml.compile(**kwargs)

        
        if CONFIG.build.rss:
            rss_link = query(ast, "link[type*=rss]")
            if rss_link is not None:
                rss_link.properties.update({
                    "type": "application/rss+xml",
                    "rel": "alternate",
                    "href": Path(CONFIG.site.base_url).joinpath(CONFIG.site.root, "feed.xml")
                })

        # Fix href and src links
        root = "/" + CONFIG.site.root.strip("/")
        for link_type in ["href", "src", "xlink:href"]:
            for node in query_all(ast, f"[{link_type}^=/]"):
                if not node[link_type].startswith(root):
                    node[link_type] = root + node[link_type]
        
        phml.ast = ast
        return phml.render(**kwargs)


class Static(File):
    """Static file representation. These files are not rendered but are still moved to the
    appropriate directory.
    """
    def __init__(self, path: str, ignore: str = "") -> None:
        super().__init__(path, ignore, True)

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

        dest = Path(dest_dir).joinpath(self._dest.strip("/"))
        original = Path(self.root).joinpath(self.path.strip("/"))

        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            copyfile(original, dest)
        except SameFileError:
            pass

class Layout(File, Linker):
    """Layout representation of a file."""

    parent: Layout | None
    """The parent layout to inherit from."""

    def __init__(self, path: str, ignore: str = "") -> None:
        File.__init__(self, path, ignore)
        Linker.__init__(self)
        self.parent: Layout | None = None
        self.linked_files = []

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
        ast = phml.parse("<Slot/>").ast

        # Start with <Slot /> element and replace the <Slot /> element with each inherited layout
        for layout in layouts:
            layout_ast = phml.load(Path(self.root).joinpath(layout.path.strip("/"))).ast

            # If it quacks like a full page, then it's a full page
            if query(layout_ast, "html") or query(layout_ast, "body"):
                Logger.warning(f"<{SAIML.parse(f'[@Fgreen]{self.full_path!r}')}> Layout must be a component not a full pages")
                return ast

            component: dict = parse_component(layout_ast)
            if query(component["component"], "Slot") is None:
                Logger.warning(f"<{SAIML.parse(f'[@Fgreen]*{self.full_path!r}')}> Layout must contain a {SAIML.parse('*<[@F#6305DC]Slot[@F] />')} element")
                return ast

            # Replace the <Slot /> element in the parent with the next layout
            substitute_component(ast.tree, ("Slot", component), VirtualPython())
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
        component: dict = parse_component(page)

        substitute_component(ast.tree, ("Slot", component), VirtualPython())
        return ast


class Component(File, Linker):
    """Represents a phml component file."""
    
    def __init__(self, path: str, ignore: str = "", unique: bool = False) -> None:
        File.__init__(self, path, ignore, unique)
        Linker.__init__(self)
        self.cname = cmpt_name_from_path(self.path)

    
class Nav:
    def __init__(self, name: str) -> None:
        self.children = []
        self.name = name

    def add(self, item):
        """Add a page or sub nav to the current nav object."""
        self.children.append(item)

    def section(self, name: str) -> Nav | None:
        """Get a specific sub nav / section by it's name."""

        for nav in self.navs:
            if nav.name == name:
                return nav
        return None

    def get(self, url: str) -> Renderable | Nav | None:
        """Get a specific page or sub nav based on it's url."""
        segments = [segment for segment in url.strip("/").split("/") if segment != ""]

        def recurse_get(segments: list[str], context: Nav, url: str) -> Renderable | Nav | None:

            pages = context.pages()
            navs = context.navs()
            new_seg = segments[0] if len(segments) > 0 else ""
            for page in pages:
                if Path(url).joinpath(new_seg).as_posix() + "/" == page.relative_url:
                    return page

            if len(segments) == 0:
                return context

            for nav in navs:
                if nav.name == segments[0]:
                    return recurse_get(segments[1:], nav, url + f"{segments[0]}/")

            return None

        if len(segments) == 0:
            for page in self.pages():
                if page.relative_url == "/":
                    return page
            return self
        else:
            return recurse_get(segments, self, "/")

    def remove(self, item: Renderable | Nav):
        """Remove a page or sub nav from the curren nav object."""
        index = -1
        if isinstance(item, Renderable):
            # TODO: recursive check url with sub navs
            for i, child in enumerate(self.children):
                if isinstance(child, Renderable) and item.relative_url == child.relative_url:
                    index = i
                    break
            error_message = f"Invalid page url {item.relative_url!r}"
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
        out = f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m \
(\x1b[34m{self.name}\x1b[0m)"
        if isinstance(self.children, list):
            for child in list(self.children):
                out += "\n" + child.print(depth + 4)
        return out

    def __str__(self) -> str:
        return self.print()

    def __repr__(self) -> str:
        return f"Nav({self.name!r}, children={len(self.children)})"

    @property
    def pages(self) -> list[Renderable]:
        """List of all renderable pages in the nav."""
        return [page for page in self.children if isinstance(page, Renderable)]
    
    @property
    def navs(self) -> list[Nav]:
        """List of all sub navs in the nav."""
        return [nav for nav in self.children if isinstance(nav, Nav)]

    def __iter__(self):
        """Iterate over the pages and sub navs in order. Starts with pages in alphabetical order
        based on their url's. Next it will iterate over the sub navs in alphabetical order based on
        sub nav name.
        """
        pages = self.pages()
        navs = self.navs()

        pages.sort(key=lambda p: p.url)
        navs.sort(key=lambda n: n.name)

        for page in pages:
            yield page

        for nav in navs:
            yield nav
