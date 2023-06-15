from pathlib import Path
from shutil import rmtree
from typing import Any
import frontmatter
from subprocess import run
from markdown import Markdown
from phml import HypertextManager, p
from phml.compiler import post_step, scoped_step
from phml.helpers import normalize_indent
from phml.nodes import AST, Element
from phml.utilities import query, query_all, remove_nodes, replace_node, walk
from saimll import SAIML, Logger
from mophidian.core import html

from mophidian.fs import FileSystem, FileType, File, TOC, Anchor
from mophidian.config import CONFIG

from re import match, sub
from mophidian.fs.core import FileState

from mophidian.fs.file_system import layouts
from mophidian.plugins import Plugin
from mophidian.plugins.pdoc import Pdoc


def flatten_children(result: TOC, children: list):
    for child in children:
        result.append(Anchor(child["name"], child["id"], child["level"]))
        if "children" in child and len(child["children"]) > 0:
            flatten_children(result, child["children"])


def head_sort(node) -> int:
    match node.tag:
        case "meta":
            return len(node.attributes)
        case "link":
            return 100 + len(node.attributes)
        case "title":
            return 200 + len(node.attributes)
        case _:
            return 400 + len(node.attributes)


MARKDOWN = Markdown(
    extensions=list(CONFIG.markdown.extensions),
    extension_configs=CONFIG.markdown.configs,
)



@scoped_step
def replace_link_root(node, *_):
    root = "/" + CONFIG.site.base.strip("/") if CONFIG.site.base.strip("/") != "" else ""
    for child in node:
        if isinstance(child, Element):
            attrs = [
                attr
                for attr in ["href", "src", "xlink:href"]
                if attr in child
                and str(child[attr]).startswith("/")
                and not str(child[attr]).startswith(root)
            ]
            for attr in attrs:
                new_link = Path(str(child[attr])).as_posix().lstrip("/")
                child[attr] = f"{root}/{new_link}"


@post_step
def save_links_used(ast, _components, _context, results):
    if "links" not in results:
        results["links"] = []

    head = query(ast, "head")
    if head is not None:
        for node in walk(head):
            if isinstance(node, Element):
                for attr in ["href", "src", "xlink:href"]:
                    if attr in node.attributes:
                        results["links"].append(node.attributes[attr])


def _build_attributes(attributes: dict) -> dict:
    """Build the props from the dynamic configuration options."""

    props = {}
    for attribute in attributes:
        if isinstance(attributes[attribute], list):
            props[attribute] = " ".join(attributes[attribute])
        elif isinstance(attributes[attribute], (str, int, float)) and not isinstance(
            attributes[attribute], bool
        ):
            props[attribute] = str(attributes[attribute])
        else:
            props[attribute] = attributes[attribute]
    return props


class Compiler:
    __slots__ = (
        "phml",
        "gcontext",
        "config",
        "file_system",
        "public",
        "components",
        "scripts",
        "nav",
        "root",
        "plugins"
    )

    def __init__(self):
        self.phml: HypertextManager = HypertextManager()

        self.file_system: FileSystem = FileSystem(CONFIG.paths.files).glob("**/*")
        self.public: FileSystem = FileSystem(CONFIG.paths.public).glob("**/*")
        self.components: FileSystem = FileSystem(CONFIG.paths.components).glob(
            "**/*.phml"
        )
        self.scripts: FileSystem = FileSystem(CONFIG.paths.scripts).glob("**/*.py")

        for component in self.components.walk_files():
            self.phml.add(component.path, ignore=component.ignore)
            component.context["cname"] = self.phml.components.generate_name(
                component._path_.as_posix(), component.ignore
            )

        for script in self.scripts.iter(FileType.File):
            self.phml.add_module(
                script.path, base="moph", ignore=self.scripts.root.ignore
            )

        self.phml.compiler.add_step(replace_link_root, "scoped")
        self.phml.compiler.add_step(save_links_used, "post")

        self.gcontext = {"files": self.file_system, "public": self.public}
        self.root = html()

        self.plugins = []
        for plugin, config in CONFIG.build.plugins.items():
            match plugin:
                case "pdoc":
                    if isinstance(config, bool):
                        config = {}
                    self.plugins.append(Pdoc(config))

    def _update_links_(self, file: File, results: dict[str, Any]):
        if "components" in results:
            new = results["components"]
            if "components" in file.context:
                for nc in filter(lambda n: n not in new, file.context["components"]):
                    cmpt = self.components.by_context("cname", nc)
                    if cmpt is not None:
                        cmpt.unlink(file)
                file.context["components"] = new
                new = list(filter(lambda n: n not in file.context["components"], new))
            else:
                file.context["components"] = new

            for component in new:
                cmpt = self.components.by_context("cname", component)
                if cmpt is not None:
                    cmpt.link(file)

        if "used_vars" in results:
            # Create update event links if a page uses the files or public files
            if "files" in results["used_vars"]:
                self.file_system.link(file)
            if "public" in results["used_vars"]:
                self.public.link(file)

            if "used_vars" in file.context:
                if (
                    "public" not in results["used_vars"]
                    and "public" in file.context["used_vars"]
                ):
                    self.public.unlink(file)
                if (
                    "files" not in results["used_vars"]
                    and "files" in file.context["used_vars"]
                ):
                    self.file_system.unlink(file)

        if "links" in results:
            for link in results["links"]:
                link = link.lstrip(".").strip("/")
                if (l := self.public.search(link)) is not None and isinstance(l, File):
                    l.link(file)
                elif (l := self.file_system.search(link)) is not None and isinstance(
                    l, File
                ):
                    l.link(file)

    def _write_static_(self, dirty: bool):
        for file in self.public.walk_files():
            if file.state == FileState.Force or (
                file.state
                in [
                    FileState.New,
                    FileState.Modified,
                ]
                and (dirty or file.is_modified())
            ):
                file.dest().write_text(file.get_content())

    def _compile_pages_(self, dirty: bool):
        for file in self.file_system.walk_files():
            if file.state == FileState.Force or (
                file.state in [FileState.New, FileState.Modified]
                or (dirty or file.is_modified())
            ):
                match file.file_type():
                    case FileType.Page:
                        self._page_(file)
                    case FileType.Markdown:
                        self._markdown_(file)
                    case FileType.Static:
                        self._static_(file)
                self._update_links_(file, self.phml.compiler.results)
            file.state = FileState.NC

    def _run_pre_build_scripts_(self, run: bool):
        if run and len(CONFIG.build.commands.pre) > 0:
            for command in CONFIG.build.commands.pre:
                key = list(command.keys())[0]
                Logger.Message(SAIML.parse(f"  \[[@Fmagenta]{key}[@F]\] {command[key]}"))

    def _run_post_build_scripts_(self, run: bool):
        if run and len(CONFIG.build.commands.post) > 0:
            Logger.custom("Post build commands...", label="▮", clr="magenta").Message
            for command in CONFIG.build.commands.post:
                key = list(command.keys())[0]
                Logger.Message(f"[{key}] \x1b[33m{command[key]}\x1b[39m")

    def _pre_plugins_(self):
        if len(self.plugins) > 0:
            for plugin in self.plugins:
                if "pre" in plugin:
                    Logger.Message(SAIML.parse(f"  \[[@Fmagenta]PLUGIN[@F]\] {plugin.__class__.__name__.lower()}"))
                    plugin.pre(CONFIG)

    def _post_plugins_(self):
        for plugin in self.plugins:
            if "post" in plugin:
                Logger.Message(SAIML.parse(f"  \[[@Fmagenta]PLUGIN[@F]\] {plugin.__class__.__name__.lower()}"))
                plugin.post(CONFIG)

    def refresh(self, dirty: bool = False):
        self._compile_pages_(dirty)
        self._write_static_(dirty)

    def build(self, dirty: bool = False, scripts: bool = False):
        if dirty:
            try:
                rmtree(CONFIG.paths.out.strip("/"))
            except:
                pass

        Logger.custom("Pre Build", label="▮", clr="magenta").Message
        self._pre_plugins_()
        self._run_pre_build_scripts_(scripts)

        Logger.Custom("Building website...", label="▮", clr="cyan")
        Path(CONFIG.paths.out).mkdir(parents=True, exist_ok=True)
        self.refresh(dirty)

        Logger.custom("Post Build", label="▮", clr="magenta").Message
        self._run_post_build_scripts_(scripts)
        self._post_plugins_()
        Logger.Custom("Build Complete", label="▮", clr="green")

    def _page_(self, file: File):
        lcontext = {"title": file.title}
        self.phml.load(file._path_)
        self.phml.load(file._path_)
        path = file.dest().as_posix()
        self.phml._ast = self._compile_layout_(file, self.phml.ast)
        self.phml.write(path, **self.gcontext, **lcontext)

    def _static_(self, file: File):
        file.dest().parent.mkdir(parents=True, exist_ok=True)
        file.dest().write_text(file.get_content())

    def _markdown_(self, file: File):
        post = frontmatter.load(file._path_)
        metadata, content = post.metadata, post.content
        content = MARKDOWN.reset().convert(content)

        # Get the attributes for the wrapper from the config
        props: dict[str, str] = _build_attributes(CONFIG.markdown.wrapper.attributes)

        lcontext = {
            "toc": self._parse_markdown_toc_(getattr(MARKDOWN, "toc_tokens", [])),
            "title": self._get_markdown_title_(content) or file.title,
            **metadata,
        }

        page = self._compile_layout_(
            file,
            p(
                p(
                    CONFIG.markdown.wrapper.tag,
                    props,
                    *self.phml.parse(content).ast.children,
                )
            ),
        )

        if page is not None:
            self.phml._ast = page
            path = file.dest().as_posix()
            self.phml.write(path, **self.gcontext, **lcontext)

    def _compile_head_(self, head: Element | None, ast: AST):
        if head is not None and "Head" not in self.phml.components:
            # Reset head tags children as they will be re ordered later
            to_head: list[Element] = [*head.children]
            head.children = []

            # Find every 'Head' tag and pull out the nested tags
            for child in query_all(ast, "Head"):
                to_head.extend(child.children)

            # Remove 'Head' tags from ast
            remove_nodes(ast, "Head")

            # Sort and put same tags together
            to_head.sort(key=head_sort)

            # Add all tags to head tag
            head.extend(to_head)

    def _compile_layout_(self, file: File, ast: AST) -> AST:
        # Base html template
        root = self.phml.parse(self.root).ast

        # Style a script tags so the contents can be combined
        styles = []
        scripts = []

        # head tag so all tags that go in the head can be combined and sorted
        head = query(root, "head")

        # For every layout for the current file, apply the layout in order
        for layout in layouts(file):
            lyt_ast = self.phml.parse(layout.get_content()).ast

            # Remove style and script tags to combine into one tag
            styles.extend(query_all(lyt_ast, "style"))
            scripts.extend(query_all(lyt_ast, "script"))
            remove_nodes(lyt_ast, "style", False)
            remove_nodes(lyt_ast, "script", False)

            # Combine Head tags into head tag
            self._compile_head_(head, lyt_ast)

            # Replace layout into the current ast's Slot tag
            if query(lyt_ast, "Slot") is not None:
                replace_node(root, "Slot", lyt_ast.children)
            else:
                print(f"{layout._path_.as_posix()!r} must contain a <Slot /> element")

        # Combine style and script tags
        if len(styles) > 0:
            out = ""
            for style in styles:
                out += f"\n{normalize_indent(style[0].content, 0)}"
            query(root, "head").append(p("style", out))

        if len(scripts) > 0:
            out = ""
            for script in scripts:
                out += f"\n{normalize_indent(script[0].content, 0)}"
            query(root, "head").append(p("script", out))

        # Combine Head tag into head tag for File ast
        self._compile_head_(head, ast)
        # Add file ast to current layout
        replace_node(root, "Slot", ast.children)
        return root

    def _get_markdown_title_(self, content: str) -> str | None:
        """Iterate lines and look for line starting with `#` or a line containing multiple `-`"""
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip() != "":
                header = match(r"(?P<hash>\s*# *.+)|(?P<block>=+)", line)
                if header is not None:
                    header = header.groupdict()
                    if header["hash"] is not None and header["hash"].strip() != "":
                        return sub(r" *# *", "", header["hash"]).strip()
                    if (
                        header["block"] is not None
                        and i > 0
                        and lines[i - 1].strip() != ""
                    ):
                        return lines[i - 1].strip()
        return None

    def _parse_markdown_toc_(self, toc: list):
        """Parse the toc structure from the markdown parser and construct a toc object."""
        result = TOC()

        for link in toc:
            result.append(Anchor(link["name"], link["id"], link["level"]))
            if "children" in link and len(link["children"]) > 0:
                flatten_children(result, link["children"])

        result
