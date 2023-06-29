from pathlib import Path
import socket
from time import sleep

from watchserver import LiveCallback, LiveServer, ServerPath
from saimll import SAIML, Log, LogLevel, Logger, style

from mophidian.config import CONFIG
from .compiler import Compiler

def is_public(path) -> bool:
    """Check if the path is a static/public path."""
    return bool(path.startswith(CONFIG.paths.public.strip("/")))


def is_file(path) -> bool:
    """Check if the path is a file/page path."""
    return bool(path.startswith(CONFIG.paths.files.strip("/")))


def is_component(path) -> bool:
    """Check if the path is a component path."""
    obj = Path(path)
    return bool(
        path.startswith(CONFIG.paths.components.strip("/")) and obj.suffix == ".phml"
    )

# TODO: Add update, create, and delete logic for python script files
def is_script(path) -> bool:
    return bool(path.startswith(CONFIG.paths.scripts.strip("/")))


class Callbacks(LiveCallback):
    """Live server callback and file management."""

    def __init__(self, scripts: bool = True) -> None:
        # Initialize the logger to only log warnings or custom logs.
        self.logger = Log(level=LogLevel.WARNING)
        self.compiler = Compiler()

        # Build website
        self.compiler.build(True, scripts)

        # Map for fast indexing and logic checking of existing files
        self.files = {
            file.path: file for file in self.compiler.file_system.files()
        }
        self.public = {file.path: file for file in self.compiler.public.files()}
        self.components = {
            file.path: file for file in self.compiler.components.files()
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
        self.logger.Debug(style("↻", fg="magenta", bold=True), ", ".join(paths))

    def create(self, _: str, file: str) -> list[str]:
        if is_public(file):
            self.create_public(file)
            self.log_reload("**/*")
            return ["**"]

        if is_file(file):
            self.create_file(file)
            self.log_reload("**/*")
            return ["**"]

        if is_component(file):
            self.create_component(file)
            self.log_reload("**/*")
            return ["**"]
        return []

    def update(self, _: str, file: str) -> list[str]:
        if is_public(file):
            self.update_public(file)
            self.log_reload("**/*")
            return ["**"]

        if is_file(file):
            self.update_file(file)
            self.log_reload("**/*")
            return ["**"]

        if is_component(file):
            return self.update_component(file)

        return []

    def remove(self, _: str, file: str) -> list[str]:
        if is_public(file):
            self.remove_public(file)
            self.log_reload("**/*")
            return ["**"]

        if is_file(file):
            return self.remove_file(file)

        if is_component(file):
            return self.remove_component(file)

        return []

    def update_file(self, path: str):
        """Update and rerender a given page."""
        if path in self.files:
            file = self.files[path]
            file.update()
            self.log_update(path=file.url())
            self.compiler.refresh()

    def update_component(self, path: str):
        """Update a given component and all linked pages."""
        file = self.components.get(path, None)

        reload_urls = []
        if file is not None:
            self.compiler.phml.add(file.path, ignore=file.ignore)
            self.log_update(cmpt=self.compiler.phml.components.generate_name(file.path, file.ignore))
            for page in file.linked:
                reload_urls.append(ServerPath(page.url()).lstrip().posix())
            self.compiler.refresh()

        self.log_reload(*reload_urls)
        return reload_urls

    def update_public(self, path: str):
        """Update a given static file and re-write it to dest."""
        if path in self.public:
            file = self.public[path]
            self.log_update(path=file.url())
            self.compiler.refresh()

    def create_file(self, path: str):
        """Update and rerender a given page."""
        file = self.compiler.file_system.push(path)
        if file is not None:
            self.files[file.path] = file
            self.log_reload("**/*")
            self.compiler.refresh()
            return ["**"]

    def create_component(self, path: str):
        """Update a given component and all linked pages."""
        file = self.compiler.components.push(path)
        if file is not None:
            self.components[file.path] = file
            self.compiler.phml.add(file.path, ignore=file.ignore)
            self.log_create(cmpt=self.compiler.phml.components.generate_name(file.path, file.ignore))

    def create_public(self, path: str):
        """Update a given static file and re-write it to dest."""
        file = self.compiler.public.push(path)
        if file is not None:
            self.public[file.path] = file
            self.log_create(path=file.url())
            self.compiler.refresh()

    def remove_public(self, path: str):
        """Remove a static file and its 'rendered' file."""
        file = self.public.pop(path, None)
        if file is not None:
            file.delete()
            self.log_delete(path=file.url())
            self.compiler.refresh()

    def remove_file(self, path: str):
        """Remove a given page."""
        file = self.files.pop(path, None)

        if file is not None:
            file.delete()
            self.log_delete(path=file.url())
            self.compiler.refresh()

        self.log_reload("**/*")
        return ["**"]

    def remove_component(self, path: str):
        """Remove a given component and update linked pages."""
        file = self.components.pop(path, None)

        reload_urls = []
        if file is not None:
            tag = self.compiler.phml.components.generate_name(file.path, file.ignore)
            file.delete()
            self.log_delete(cmpt=tag)
            for page in file.linked:
                page.event()
                reload_urls.append(ServerPath(page.url()).lstrip().posix())
            self.compiler.phml.remove(tag)
            self.compiler.refresh()

        self.log_reload(*reload_urls)
        return reload_urls

def server_start(server: LiveServer, expose: bool = False):
    """Start a server and print the started message with hosts."""
    # Get port and network information
    socket_server = server.server_thread.server
    IPHostName = socket.gethostname()

    url = socket_server.url()
    network_ip = socket_server.url(socket.gethostbyname(IPHostName))
    network_host_name = socket_server.url(IPHostName)

    network_message = f"use {style('--host', fg='yellow')} to expose"
    if expose:
        network_message = (
            f"{SAIML.parse(f'[@Fyellow~{network_ip}]{network_ip}')}\n"
            + f"{' '*17}{SAIML.parse(f'[@Fyellow~{network_host_name}]{network_host_name}')}"
        )

    # Start server and print started message
    server.start()
    (
        Logger.custom(
            style("Mophidian", fg="black", bg=(166, 218, 149)),
            "server has started",
            label="🚀",
            clr="white",
        )
        .message()
        .message(
            f"{' '*6}▍ {style('Local', fg='cyan')}:   {SAIML.parse(f'[@Fyellow~{url}]{url}')}"
        )
        .message(f"{' '*6}▍ {style('Network', fg='cyan')}: {network_message}")
        .Message()
    )


def server_shutdown(server: LiveServer):
    """Shutdown a server and print the shutdown message."""
    Logger.Custom(
        style("Mophidian", fg="black", bg=(166, 218, 149)),
        "Shutting down...",
        label="🚀",
        clr="white",
    )
    server.stop()


def run_server(server: LiveServer, expose: bool = False):
    """Run a live reloading server."""

    try:
        server_start(server, expose)
        while True:
            sleep(1)
    except KeyboardInterrupt:
        server_shutdown(server)
