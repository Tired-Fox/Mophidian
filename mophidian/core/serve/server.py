from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import socket
from pathlib import Path
import posixpath
from threading import Thread
from time import sleep
from typing import Any
import webbrowser
from re import match

from watchdog.observers import Observer
from teddecor import TED, style, Log, LogLevel, Logger
from phml import PHML

from mophidian import states, CONFIG
from mophidian.core import render_pages, write_static_files, build
from mophidian.file_system import (
    File,
    Directory,
    Renderable,
    Layout,
    Component,
    FileState,
    Static,
    Page,
    Markdown
)
from .watchdog import Handler

PORT_RANGE = [49200, 65535]

# Reference: https://docs.python.org/3/library/http.server.html

hostName = "localhost"
serverPort = 8080
WATCHLABEL = "Server"
WATCHUPDATE = "[@Fyellow]Updated[@F]"
WATCHCREATE = "[@Fcyan]Created[@F]"
WATCHDELETE = "[@Fmagenta]Removed[@F]"

class LiveServer:
    
    def __init__(
        self, 
        host: str = "localhost",
        port=PORT_RANGE[0],
        open: bool = False,
        expose_host: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.open = open
        self.expose_host = expose_host
            
        callbacks = {
            "update": {
                "page": self.update_page,
                "layout": self.update_layout,
                "component": self.update_component,
                "static": self.update_static,
            },
            "remove": {
                "page": self.remove_page,
                "layout": self.remove_layout,
                "component": self.remove_component,
                "static": self.remove_static,
            },
            "create": {
                "page": self.create_page,
                "layout": self.create_layout,
                "component": self.create_component,
                "static": self.create_static,
            }
        }

        # Assign callbacks that handle updating the files and restarting the server
        event_handler = Handler(callbacks)
        self.watchdog = Observer()

        # Watch the source, component, and public directories
        self.watchdog.schedule(event_handler, CONFIG.site.source, recursive=True)
        self.watchdog.schedule(event_handler, CONFIG.site.components, recursive=True)
        self.watchdog.schedule(event_handler, CONFIG.site.public, recursive=True)

        self.file_system = Directory("")
        self.static_files = Directory("")
        self.component_files = Directory("")
        self.phml = PHML()

    def run(self):
        """Start the server and file watcher. Creates infinit loop that is interuptable."""
        self.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        """Start the server and file watcher."""
        (
            self.file_system,
            self.static_files,
            self.component_files,
            self.phml
        ) = build(live_reload=True)

        self.files = {file.full_path: file for file in self.file_system.files()}
        self.statics = {file.full_path: file for file in self.static_files.files()}
        self.components = {file.full_path: file for file in self.component_files.files()}

        self.server = ServerThread(
            self.host,
            self.port,
            self.open,
            self.expose_host,
            daemon=True,
            files=self.files
        )

        self.server.start()
        self.watchdog.start()
        self.logger = Log(level=LogLevel.INFO)

    def stop(self):
        """Stop the server and file watcher."""
        self.server.stop()
        self.watchdog.stop()

    def render_pages(self):
        render_pages(
            self.file_system,
            self.static_files,
            self.component_files,
            states["dest"],
            self.phml,
            self.file_system.build_nav(),
            live_reload=True,
        )

    def write_static(self):
        write_static_files(self.file_system, self.static_files, states["dest"])

    def update_layout(self, path: str):
        """Update a given layout and all linked pages."""
        path = path.replace("\\", "/")
        obj = self.files.get(path, None)

        if obj is not None and isinstance(obj, Layout):
            obj.state = FileState.UPDATED
            self.file_system.build_hierarchy()
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(TED.parse(f"{WATCHUPDATE} [@Fgreen$]{page.relative_url}"), label=WATCHLABEL)
            self.render_pages()

    def update_page(self, path: str):
        """Update and rerender a given page."""
        path = path.replace("\\", "/")
        obj = self.files.get(path, None)

        if obj is not None and isinstance(obj, Renderable):
            obj.state = FileState.UPDATED
            self.file_system.build_hierarchy()
            self.render_pages()
            self.logger.Custom(TED.parse(f"{WATCHUPDATE} [@Fgreen$]{obj.relative_url}"), label=WATCHLABEL)

    def update_component(self, path: str):
        """Update a given component and all linked pages."""
        path = path.replace("\\", "/")
        obj = self.components.get(path)

        if obj is not None and isinstance(obj, Component):
            self.phml.add((obj.cname, obj.full_path))
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(TED.parse(f"{WATCHUPDATE} [@Fgreen$]{page.relative_url}"), label=WATCHLABEL)
            self.render_pages()

    def update_static(self, path: str):
        """Update a given static file and re-write it to dest."""
        path = path.replace("\\", "/")
        obj = self.files.get(path, None)

        if obj is None:
            obj = self.statics.get(path, None)

        if obj is not None and isinstance(obj, Static):
            obj.state = FileState.UPDATED
            self.write_static()
            self.logger.Custom(TED.parse(f"{WATCHUPDATE} [@Fgreen$]{obj.relative_url}"), label=WATCHLABEL)

    def create_layout(self, path: str):
        """Update a given layout and all linked pages."""
        path = path.replace("\\", "/")
        new_layout = Layout(path, ignore=CONFIG.site.source)
        
        self.file_system.add(new_layout)
        self.files[new_layout.full_path] = new_layout
        self.file_system.build_hierarchy()
        
        for page in new_layout.linked_files:
            page.state = FileState.UPDATED
            self.logger.Custom(TED.parse(f"{WATCHUPDATE} [@Fgreen$]{new_layout.relative_url})"), label=WATCHLABEL)
        
        self.render_pages()

    def create_page(self, path: str):
        """Update and rerender a given page."""
        path = path.replace("\\", "/")
        pPage = Path(path)
        new_page = None
        if pPage.suffix == ".phml":
            new_page = Page(path, ignore=CONFIG.site.source)
        elif pPage.suffix in [".md", ".mdx"]:
            new_page = Markdown(path, ignore=CONFIG.site.source)
        
        if new_page is not None:
            new_page.state = FileState.UPDATED
            self.file_system.add(new_page)
            self.files[new_page.full_path] = new_page
            self.file_system.build_hierarchy()
            self.render_pages()
            self.logger.Custom(TED.parse(f"{WATCHCREATE} [@Fgreen$]{new_page.relative_url}"), label=WATCHLABEL)

    def create_component(self, path: str):
        """Update a given component and all linked pages."""
        path = path.replace("\\", "/")
        new_component = Component(path, ignore=CONFIG.site.components)

        self.component_files.add(new_component)
        self.components[new_component.full_path] = new_component
        try:
            self.phml.add((new_component.cname, new_component.full_path))
        except Exception as error:
            self.logger.Error(str(error))
        self.logger.Custom(TED.parse(f"{WATCHCREATE} component <[@F#6305DC$]{new_component.cname}[@F] />"), label=WATCHLABEL)

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
            self.logger.Custom(TED.parse(f"{WATCHCREATE} [@Fgreen$]{new_static.relative_url}"), label=WATCHLABEL)
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
            self.logger.Custom(TED.parse(f"{WATCHDELETE} [@Fgreen$]{obj.relative_url}"), label=WATCHLABEL)

    def remove_layout(self, path: str):
        """Remove a given layout and update all linked pages."""
        path = path.replace("\\", "/")
        obj = self.files.pop(path, None)

        if obj is not None and isinstance(obj, Layout):
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(TED.parse(f"{WATCHDELETE} [@Fgreen$]{page.relative_url}"), label=WATCHLABEL)
            self.file_system.remove(obj.full_path)
            self.file_system.build_hierarchy()
            self.render_pages()

    def remove_page(self, path: str):
        """Remove a given page."""
        path = path.replace("\\", "/")
        obj = self.files.pop(path, None)

        if obj is not None and isinstance(obj, Renderable):
            obj.state = FileState.DELETED
            self.render_pages()
            self.logger.Custom(TED.parse(f"{WATCHDELETE} [@Fgreen$]{obj.relative_url}"), label=WATCHLABEL)

    def remove_component(self, path: str):
        """Remove a given component and update linked pages."""
        path = path.replace("\\", "/")
        obj = self.components.pop(path, None)

        if obj is not None and isinstance(obj, Component):
            self.logger.Custom(TED.parse(f"{WATCHDELETE} component <[@F#6305DC$]{obj.cname}[@F] />"), label=WATCHLABEL)
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(TED.parse(f"{WATCHUPDATE} [@Fgreen$]{page.relative_url}"), label=WATCHLABEL)
            self.phml.remove(obj.cname)
            self.component_files.remove(obj.full_path)
            self.render_pages()

FileSystem = dict[str, File]
StaticFiles = Directory

class ServerThread(Thread):
    """Thread for the server to allow for serve_forever without interfering with the main thread."""

    def __init__(
        self,
        host: str = "localhost",
        port=PORT_RANGE[0],
        open: bool = False,
        expose_host: bool = False,
        files: FileSystem | None = None,
        *args,
        **kwargs
    ):
        super(ServerThread, self).__init__(*args, **kwargs)
        self.server = Server(host, port, open, expose_host, files=files)

    def data(self) -> tuple:
        return self.server.host, self.server.server_port, self.server.open, self.server.expose_host

    def run(self) -> None:
        self.server.start()

    def restart(self):
        self.server.shutdown()
        self.server.server_close()
        self.server.server_activate()
        self.server.serve_forever()

    def stop(self):
        self.server.stop()

    def stopped(self):
        return self.server.active()

class ServiceHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server, *, directory: str | None = "") -> None:
        if Path("dist").is_dir():
            directory = "dist/"
        super().__init__(request, client_address, server, directory=directory)
        self.logger = Log(level=LogLevel.ERROR)

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        custom_page = Path("dist/").joinpath(CONFIG.site.root, f"{code}.html")
        if custom_page.is_file():
            self.send_response(code)
            self.end_headers()
            with open(custom_page, "r", encoding="utf-8") as custom_error_file:
                self.wfile.write(custom_error_file.read().encode("utf-8"))
            return
        return super().send_error(code, message, explain)

    def do_GET(self) -> None:
        path = self.translate_path(self.path).lstrip("dist/").replace("\\", "/")
        live_reload = match(r"/?livereload/(\d+)/(.+)", path)

        if live_reload is not None:
            _expected_epoch, file_path = live_reload.groups()
            try:
                if file_path == "undefined":
                    # Force reload the page to attempt to get the page to send valid information
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(f"{int(_expected_epoch) + 1}", "utf-8"))
                    return
                else:
                    # Validate with files build epoch
                    if self.server.files is not None:
                        file = self.server.files.get(file_path, None)
                        if file is not None:
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(bytes(f"{int(file.epoch)}", "utf-8"))
                            return
            finally:
                # Default to no change for file
                self.send_response(200)
                self.end_headers()
                self.wfile.write(bytes(f"{int(_expected_epoch) - 1}", "utf-8"))
                return

        # If not live-reload path then do default do_GET
        super().do_GET()

    def log_request(self, code: int | str = "", size: int | str = "") -> None:
        # TODO: Custom request messages
        pass

    def log_error(self, format: str, *args: Any) -> None:
        # TODO: Custom error messages
        pass

class Server(ThreadingHTTPServer):
    def __init__(
        self,
        host: str = "localhost",
        port=PORT_RANGE[0],
        open: bool = False,
        expose_host: bool = False,
        files: FileSystem | None = None,
    ):

        super().__init__((host, port), ServiceHandler)
        self.open = open
        self.host = host
        self.expose_host = expose_host
        self.is_active = False
        self.logger = Log(level=LogLevel.INFO)
        self.files = files
        self.full_url = f"http://{host}:{port}/"
        
    def serve_forever(self, poll_interval: float = 0.5) -> None:
        self.is_active = True
        return super().serve_forever(poll_interval)

    def shutdown(self) -> None:
        self.is_active = False
        super().shutdown()
        self.server_close()
    
    def active(self) -> bool:
        return self.is_active

    def url(self, host: str) -> str:
        return posixpath.join(f"http://{host}:{self.server_port}/", CONFIG.site.root)
    
    def _log_start(self):
        IPHostName = socket.gethostname()

        url = self.url(self.host)
        network_ip = self.url(socket.gethostbyname(IPHostName))
        network_host_name = self.url(IPHostName)

        network_message = f"use {style('--host', fg='yellow')} to expose"
        if self.expose_host:
            network_message = (
                f"{TED.parse(f'[@Fyellow~{network_ip}]{network_ip}')}\n"
                + f"{' '*17}{TED.parse(f'[@Fyellow~{network_host_name}]{network_host_name}')}"
            )
        (
            self.logger.custom(
                style("Mophidian", fg="white", bg=(166,218,149)),
                "server has started",
                label="🚀",
                clr="white"
            )
            .message()
            .message(
                f"{' '*6}▍ {style('Local', fg='cyan')}:   {TED.parse(f'[@Fyellow~{url}]{url}')}"
            )
            .message(f"{' '*6}▍ {style('Network', fg='cyan')}: {network_message}")
            .Message()
        )
        
    def _log_stop(self):
        self.logger.message().Custom(
            style("Mophidian", fg="white", bg=(166,218,149)),
            "Shutting down...",
            label="🚀",
            clr="white"
        )

    def start(self):
        # Log the url of the server
        self._log_start()
        Logger.flush()

        # if auto open then open in browser
        if self.open:
            webbrowser.open_new_tab(self.url(self.host))

        # start server
        self.serve_forever()

    def stop(self):
        self._log_stop()
        self.shutdown()
        self.server_close()