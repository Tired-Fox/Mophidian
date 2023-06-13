from functools import cache
import os
from pathlib import Path
from shutil import rmtree
from typing import Any, Literal
import frontmatter
from markdown import Markdown
from phml import HypertextManager, p
from phml.helpers import normalize_indent
from phml.nodes import AST, Node
from phml.utilities import query, query_all, remove_nodes, replace_node
from mophidian.core import html

from mophidian.fs import FileSystem, FileType, File, TOC, Anchor
from mophidian.config import CONFIG

from re import match, sub
from mophidian.fs.core import FileState

from mophidian.fs.file_system import layouts

MARKDOWN = Markdown(
    extensions=list(CONFIG.markdown.extensions),
    extension_configs=CONFIG.markdown.configs,
)


def _build_attributes(attributes: dict) -> dict:
    """Build the props from the dynamic configuration options."""

    props = {}
    for attribute in attributes:
        if isinstance(attributes[attribute], list):
            props[attribute] = " ".join(attributes[attribute])
        elif isinstance(attributes[attribute], (str, int, float)):
            props[attribute] = str(attributes[attribute])
        elif isinstance(attributes[attribute], bool):
            props[attribute] = "yes" if attributes[attribute] else "no"
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
    )

    def __init__(self):
        self.phml: HypertextManager = HypertextManager()

        self.file_system: FileSystem = FileSystem(CONFIG.paths.files).glob("**/*")
        self.public: FileSystem = FileSystem(CONFIG.paths.public).glob("**/*")
        self.components: FileSystem = FileSystem(CONFIG.paths.components).glob(
            "**/*.phml"
        )
        self.scripts: FileSystem = FileSystem(CONFIG.paths.scripts).glob("**/*.py")

        for component in self.components.walk(FileType.File):
            self.phml.add(component.path, ignore=component.ignore)
            component.context["cname"] = self.phml.components.generate_name(
                component._path_.as_posix(), component.ignore
            )

        for script in self.scripts.iter(FileType.File):
            self.phml.add_module(
                script.path, base="moph", ignore=self.scripts.root.ignore
            )

        self.gcontext = {"files": self.file_system, "public": self.public}
        self.root = html()

        out = Path(CONFIG.paths.out)
        if out.is_dir():
            rmtree(CONFIG.paths.out)

    def _update_results_(self, file: File, results: dict[str, Any]):
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

    def _file_system_(self, dirty: bool):
        for file in self.file_system.walk(FileType.File):
            if (
                file.state in [FileState.Force, FileState.New]
                or (dirty or file.is_modified())
                and file.state == FileState.Modified
            ):
                match file.file_type():
                    case FileType.Page:
                        self._page_(file)
                    case FileType.Markdown:
                        self._markdown_(file)
                    case FileType.Static:
                        self._static_(file)
                self._update_results_(file, self.phml.compiler.results)
            file.state = FileState.NC

    def build(self, dirty: bool = False):
        self._file_system_(dirty)

    def _page_(self, file: File):
        lcontext = {"title": file.title}
        self.phml.load(file._path_)
        self.phml.load(file._path_)
        path = (Path(file.url(CONFIG.paths.out)) / "index.html").as_posix().lstrip("/")
        self.phml._ast = self._build_page_(file, self.phml.ast.children)
        self.phml.write(path, **self.gcontext, **lcontext)

    def _static_(self, file: File):
        path = Path(file.url(CONFIG.paths.out).lstrip("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file.get_content())

    def _markdown_(self, file: File):
        post = frontmatter.load(file._path_)
        metadata, content = post.metadata, post.content
        content = MARKDOWN.reset().convert(content)

        # Get the attributes for the wrapper from the config
        props: dict[str, str] = _build_attributes(CONFIG.markdown.wrapper.attributes)

        lcontext = {
            "toc": self._parse_toc_(getattr(MARKDOWN, "toc_tokens", [])),
            "title": self._markdown_title(content) or file.title,
            **metadata,
        }

        page = self._build_page_(
            file,
            p(
                CONFIG.markdown.wrapper.tag,
                props,
                *self.phml.parse(content).ast.children,
            ),
        )

        if page is not None:
            self.phml._ast = page
            path = (
                (Path(file.url(CONFIG.paths.out)) / "index.html").as_posix().lstrip("/")
            )
            self.phml.write(path, **self.gcontext, **lcontext)

    def _build_page_(self, file: File, ast: Node | list[Node]) -> AST:
        root = self.phml.parse(self.root).ast
        styles = []
        scripts = []
        for layout in layouts(file):
            lyt_ast = self.phml.parse(layout.get_content()).ast

            # Remove style and script tags to combine into one tag
            styles.extend(query_all(lyt_ast, "style"))
            scripts.extend(query_all(lyt_ast, "script"))
            remove_nodes(lyt_ast, "style", False)
            remove_nodes(lyt_ast, "script", False)

            if query(lyt_ast, "Slot") is not None:
                replace_node(root, "Slot", lyt_ast.children)
            else:
                print(f"{layout._path_.as_posix()!r} must contain a <Slot /> element")

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

        replace_node(root, "Slot", ast)
        return root

    def _markdown_title(self, content: str) -> str | None:
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

    def _parse_toc_(self, toc: list):
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

        result
