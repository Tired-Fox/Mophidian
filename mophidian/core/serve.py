from pathlib import Path

from watchserver import LiveCallback, ServerPath
from saimll import SAIML, Log, LogLevel, style

from mophidian import CONFIG, states
from mophidian.core import render_pages, write_static_files
from mophidian.file_system import (
    Component,
    FileState,
    Layout,
    Markdown,
    Page,
    Renderable,
    Static,
)

from .build import build
from .util import REGEX


def is_static(path) -> bool:
    """Check if the path is a static path."""
    path = Path(path)
    return bool(path.suffix not in [".phml", ".md", ".mdx"])


def is_layout(path) -> bool:
    """Check if the path is a layout path."""
    obj = Path(path)
    return bool(
        path.startswith(CONFIG.site.source.strip("/"))
        and obj.suffix == ".phml"
        and REGEX["layout"]["name"].match(obj.name) is not None
    )


def is_page(path) -> bool:
    """Check if the path is a page path."""
    obj = Path(path)
    return bool(
        path.startswith(CONFIG.site.source.strip("/"))
        and obj.suffix in [".md", ".mdx", ".phml"]
        and REGEX["layout"]["name"].match(obj.name) is None
    )


def is_component(path) -> bool:
    """Check if the path is a component path."""
    obj = Path(path)
    return bool(
        path.startswith(CONFIG.site.components.strip("/")) and obj.suffix == ".phml"
    )


class Callbacks(LiveCallback):
    """Live server callback and file management."""

    def __init__(self) -> None:
        # Initialize the logger to only log warnings or custom logs.
        self.logger = Log(level=LogLevel.WARNING)

        # Build website
        self.logger.Custom("Building website...", label="▮", clr="cyan")
        (self.file_system, self.static_files, self.component_files, self.phml) = build(
            True
        )

        # Map for fast indexing and logic checking of existing files
        self.files = {file.full_path: file for file in self.file_system.files()}
        self.statics = {file.full_path: file for file in self.static_files.files()}
        self.components = {
            file.full_path: file for file in self.component_files.files()
        }

    def render_log_content(self, cmpt: str | None, path: str | None) -> str:
        """Render either component or path text for a log event."""
        return (
            SAIML.parse(f"<*[@F#6305DC$]{cmpt}[] />")
            if cmpt is not None
            else path or repr("")
        )

    def log_create(self, cmpt: str | None = None, path: str | None = None):
        """Log a create event."""
        self.logger.Message(
            style("+", fg="green", bold=True), self.render_log_content(cmpt, path)
        )

    def log_update(self, cmpt: str | None = None, path: str | None = None):
        """Log a update/modified event."""
        self.logger.Message(
            style("*", fg="yellow", bold=True), self.render_log_content(cmpt, path)
        )

    def log_delete(self, cmpt: str | None = None, path: str | None = None):
        """Log a delete event."""
        self.logger.Message(
            style("-", fg="red", bold=True), self.render_log_content(cmpt, path)
        )

    def log_reload(self, *paths: str):
        """Log a reload event."""
        self.logger.Message(
            style("↻", fg="magenta", bold=True),
            ", ".join(paths)
        )

    def create(self, root: str, file: str) -> list[str]:
        if is_static(file):
            self.create_static(file)
            self.log_reload("**/*")
            return ["**"]

        if is_page(file):
            return self.create_page(file)

        if is_layout(file):
            return self.create_layout(file)

        if is_component(file):
            self.create_component(file)
            self.log_reload("**/*")
            return ["**"]

        return []

    def update(self, root: str, file: str) -> list[str]:
        if is_static(file):
            self.update_static(file)
            self.log_reload("**/*")
            return ["**"]

        if is_page(file):
            return self.update_page(file)

        if is_layout(file):
            return self.update_layout(file)

        if is_component(file):
            return self.update_component(file)

        return []

    def remove(self, root: str, file: str) -> list[str]:
        if is_static(file):
            self.remove_static(file)
            self.log_reload("**/*")
            return ["**"]

        if is_page(file):
            return self.remove_page(file)

        if is_layout(file):
            return self.remove_layout(file)

        if is_component(file):
            return self.remove_component(file)

        return []

    def render_pages(self):
        """Re-render the site pages."""
        render_pages(
            self.file_system,
            self.static_files,
            self.component_files,
            states["dest"],
            self.phml,
            self.file_system.build_nav(),
        )

    def write_static(self):
        """Re-write all site static files."""
        write_static_files(self.file_system, self.static_files, states["dest"])

    def update_layout(self, path: str):
        """Update a given layout and all linked pages."""
        path = path.replace("\\", "/")
        obj = self.files.get(path, None)

        reload_urls = []
        if obj is not None and isinstance(obj, Layout):
            obj.state = FileState.UPDATED
            self.file_system.build_hierarchy()
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                reload_urls.append(ServerPath(page.url).lstrip().posix())
            self.render_pages()

        self.log_reload(*reload_urls)
        return reload_urls

    def update_page(self, path: str):
        """Update and rerender a given page."""
        path = path.replace("\\", "/")
        obj = self.files.get(path, None)

        if obj is not None and isinstance(obj, Renderable):
            obj.state = FileState.UPDATED
            self.file_system.build_hierarchy()
            self.render_pages()
            self.log_update(path=obj.relative_url)

        reload_urls = (
            [ServerPath(obj.url).lstrip().posix()]
            if obj is not None
            else []
        )
        self.log_reload(*reload_urls)
        return reload_urls

    def update_component(self, path: str):
        """Update a given component and all linked pages."""
        path = path.replace("\\", "/")
        obj = self.components.get(path)

        reload_urls = []
        if obj is not None and isinstance(obj, Component):
            self.phml.add((obj.cname, obj.full_path))
            self.log_update(cmpt=obj.cname)
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                reload_urls.append(ServerPath(page.url).lstrip().posix())
            self.render_pages()

        self.log_reload(*reload_urls)
        return reload_urls

    def update_static(self, path: str):
        """Update a given static file and re-write it to dest."""
        path = path.replace("\\", "/")
        obj = self.files.get(path, None)

        if obj is None:
            obj = self.statics.get(path, None)

        if obj is not None and isinstance(obj, Static):
            obj.state = FileState.UPDATED
            self.write_static()
            self.log_update(path=obj.relative_url)

    def create_layout(self, path: str):
        """Update a given layout and all linked pages."""
        path = path.replace("\\", "/")
        new_layout = Layout(path, ignore=CONFIG.site.source)

        self.file_system.add(new_layout)
        self.files[new_layout.full_path] = new_layout
        self.file_system.build_hierarchy()
        reload_urls = []
        for page in new_layout.linked_files:
            page.state = FileState.UPDATED
            reload_urls.append(ServerPath(page.url).lstrip().posix())

        self.render_pages()
        self.log_reload(*reload_urls)
        return reload_urls

    def create_page(self, path: str):
        """Update and rerender a given page."""
        path = path.replace("\\", "/")
        obj = Path(path)
        new_page = None
        if obj.suffix == ".phml":
            new_page = Page(path, ignore=CONFIG.site.source)
        elif obj.suffix in [".md", ".mdx"]:
            new_page = Markdown(path, ignore=CONFIG.site.source)

        if new_page is not None:
            new_page.state = FileState.UPDATED
            self.file_system.add(new_page)
            self.files[new_page.full_path] = new_page
            self.file_system.build_hierarchy()
            self.render_pages()
            self.log_create(path=new_page.relative_url)

        reload_urls = (
            [ServerPath(new_page.url).lstrip().posix()]
            if new_page is not None
            else []
        )

        self.log_reload(*reload_urls)
        return reload_urls

    def create_component(self, path: str):
        """Update a given component and all linked pages."""
        path = path.replace("\\", "/")
        new_component = Component(path, ignore=CONFIG.site.components)

        self.component_files.add(new_component)
        self.components[new_component.full_path] = new_component
        try:
            self.phml.add((new_component.cname, new_component.full_path))
            self.log_create(cmpt=new_component.cname)
        except Exception as error:
            self.logger.Error(str(error))

    def create_static(self, path: str):
        """Update a given static file and re-write it to dest."""
        path = path.replace("\\", "/")
        new_static = None

        if path.startswith(CONFIG.site.source):
            new_static = Static(path, ignore=CONFIG.site.source)
            self.file_system.add(new_static)
            self.files[new_static.full_path] = new_static
        elif path.startswith(CONFIG.site.public):
            new_static = Static(path, ignore=CONFIG.site.public)
            self.static_files.add(new_static)
            self.statics[new_static.full_path] = new_static

        if new_static is not None:
            self.log_create(path=new_static.relative_url)
            self.write_static()

    def remove_static(self, path: str):
        """Remove a static file and its 'rendered' file."""
        path = path.replace("\\", "/")
        obj = self.files.pop(path, None)
        if obj is None:
            obj = self.statics.pop(path, None)

        if obj is not None and isinstance(obj, Static):
            obj.state = FileState.DELETED
            self.write_static()
            self.log_delete(path=obj.relative_url)

    def remove_layout(self, path: str):
        """Remove a given layout and update all linked pages."""
        path = path.replace("\\", "/")
        obj = self.files.pop(path, None)

        reload_urls = []
        if obj is not None and isinstance(obj, Layout):
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                reload_urls.append(ServerPath(page.url).lstrip().posix())
            self.file_system.remove(obj.full_path)
            self.file_system.build_hierarchy()
            self.render_pages()

        self.log_reload(*reload_urls)
        return reload_urls

    def remove_page(self, path: str):
        """Remove a given page."""
        path = path.replace("\\", "/")
        obj = self.files.pop(path, None)

        if obj is not None and isinstance(obj, Renderable):
            obj.state = FileState.DELETED
            self.render_pages()
            self.log_delete(path=obj.relative_url)

        reload_urls = (
            [ServerPath(obj.url).lstrip().posix()]
            if obj is not None
            else []
        )

        self.log_reload(*reload_urls)
        return reload_urls

    def remove_component(self, path: str):
        """Remove a given component and update linked pages."""
        path = path.replace("\\", "/")
        obj = self.components.pop(path, None)

        reload_urls = []
        if obj is not None and isinstance(obj, Component):
            self.log_delete(cmpt=obj.cname)
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                reload_urls.append(ServerPath(page.url).lstrip().posix())
            self.phml.remove(obj.cname)
            self.component_files.remove(obj.full_path)
            self.render_pages()

        self.log_reload(*reload_urls)
        return reload_urls
