from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import socket
from pathlib import Path
import posixpath
import string
from threading import Thread
from time import sleep
from typing import Any
import webbrowser

from watchdog.observers import Observer
from teddecor import TED, style, Log, LogLevel
from phml import PHML

from mophidian import states, CONFIG
from mophidian.core import render_pages, write_static_files
from mophidian.FileSystem import Directory, Renderable, Layout, Component, FileState, Static, Page, Markdown
from .watchdog import Handler

PORT_RANGE = [49200, 65535]

# Reference: https://docs.python.org/3/library/http.server.html

# TODO: Inject his javascript into html to allow for live reloading
_SCRIPT_LIVE_RELOAD = """\
var livereload = function(epoch, requestId) {
    var req = new XMLHttpRequest();
    req.onloadend = function() {
        if (parseFloat(this.responseText) > epoch) {
            location.reload();
            return;
        }
        var launchNext = livereload.bind(this, epoch, requestId);
        if (this.status === 200) {
            launchNext();
        } else {
            setTimeout(launchNext, 3000);
        }
    };
    req.open("GET", "/livereload/" + epoch + "/" + requestId);
    req.send();
    console.log('Enabled live reload');
}
livereload(${epoch}, ${request_id});\
"""
#! Server request handler will have to be updated to handle epoc update

_LIVE_RELOAD_JS = string.Template(_SCRIPT_LIVE_RELOAD)

hostName = "localhost"
serverPort = 8080
WATCHLABEL = "Server"
WATCHUPDATE = "yellow"
WATCHCREATE = "cyan"
WATCHDELETE = "magenta"

# TODO: Use watch dog and watch for changes, if any occur stop the server and start again

class LiveServer:
    
    def __init__(
        self, 
        host: str = "localhost",
        port=PORT_RANGE[0],
        open: bool = False,
        expose_host: bool = False,
    ) -> None:
        self.server = ServerThread(host, port, open, expose_host, daemon=True)

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

    def run(
        self,
        file_system: Directory,
        static_files: Directory,
        component_files: Directory,
        phml: PHML
    ):
        """Start the server and file watcher. Creates infinit loop that is interuptable."""
        self.start(file_system, static_files, component_files, phml)
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(
        self,
        file_system: Directory,
        static_files: Directory,
        component_files: Directory,
        phml: PHML
    ):
        """Start the server and file watcher."""
        self.file_system = file_system
        self.static_files = static_files
        self.component_files = component_files
        self.phml = phml

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
            self.file_system.build_nav()
            inject=[]
        )

    def write_static(self):
        write_static_files(self.file_system, self.static_files, states["dest"])

    def update_layout(self, layout: str):
        """Update a given layout and all linked pages."""
        layout = layout.replace("\\", "/")
        obj = self.file_system.find(layout)

        if obj is not None and isinstance(obj, Layout):
            obj.state = FileState.UPDATED
            self.file_system.build_hierarchy()
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(f"Updated {page.relative_url}", clr=WATCHUPDATE, label=WATCHLABEL)
            self.render_pages()

    def update_page(self, page: str):
        """Update and rerender a given page."""
        page = page.replace("\\", "/")
        obj = self.file_system.find(page)

        if obj is not None and isinstance(obj, Renderable):
            obj.state = FileState.UPDATED
            self.file_system.build_hierarchy()
            self.render_pages()
            self.logger.Custom(f"Updated {obj.relative_url}", clr=WATCHUPDATE, label=WATCHLABEL)

    def update_component(self, component: str):
        """Update a given component and all linked pages."""
        component = component.replace("\\", "/")
        obj = self.component_files.find(component)

        if obj is not None and isinstance(obj, Component):
            self.phml.add((obj.cname, obj.full_path))
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(f"Updated {page.relative_url}", clr=WATCHUPDATE, label=WATCHLABEL)
            self.render_pages()

    def update_static(self, static: str):
        """Update a given static file and re-write it to dest."""
        static = static.replace("\\", "/")
        obj = self.file_system.find(static)

        if obj is None:
            obj = self.static_files.find(static)

        if obj is not None and isinstance(obj, Static):
            obj.state = FileState.UPDATED
            self.write_static()
            self.logger.Custom(f"Updated {obj.relative_url}", clr=WATCHUPDATE, label=WATCHLABEL)

    def create_layout(self, layout: str):
        """Update a given layout and all linked pages."""
        layout = layout.replace("\\", "/")
        new_layout = Layout(layout, ignore=CONFIG.site.source)
        
        self.file_system.add(new_layout)
        self.file_system.build_hierarchy()
        
        for page in new_layout.linked_files:
            page.state = FileState.UPDATED
            self.logger.Custom(f"Updated {new_layout.relative_url}", clr=WATCHCREATE, label=WATCHLABEL)
        
        self.render_pages()

    def create_page(self, page: str):
        """Update and rerender a given page."""
        page = page.replace("\\", "/")
        pPage = Path(page)
        new_page = None
        if pPage.suffix == ".phml":
            new_page = Page(page, ignore=CONFIG.site.root)
        elif pPage.suffix in [".md", ".mdx"]:
            new_page = Markdown(page, ignore=CONFIG.site.root)
        
        if new_page is not None:
            self.file_system.add(new_page)
            self.file_system.build_hierarchy()
            self.render_pages()
            self.logger.Custom(f"Created {new_page.relative_url}", clr=WATCHCREATE, label=WATCHLABEL)

    def create_component(self, component: str):
        """Update a given component and all linked pages."""
        component = component.replace("\\", "/")
        new_component = Component(component, ignore=CONFIG.site.components)

        self.component_files.add(new_component)
        self.phml.add((new_component.cname, new_component.full_path))
        self.logger.Custom(f"Created componennt <{new_component.cname} />", clr=WATCHCREATE, label=WATCHLABEL)

    def create_static(self, static: str):
        """Update a given static file and re-write it to dest."""
        static = static.replace("\\", "/")
        new_static = None

        if static.startswith(CONFIG.site.source):
            new_static = Static(static, ignore=CONFIG.site.source)
            self.file_system.add(new_static)
        elif static.startswith(CONFIG.site.public):
            new_static = Static(static, ignore=CONFIG.site.public)
            self.static_files.add(new_static)

        if new_static is not None:
            self.logger.Custom(f"Created {new_static.relative_url}", clr=WATCHCREATE, label=WATCHLABEL)
            self.write_static()

    def remove_static(self, static: str):
        """Remove a static file and its 'rendered' file."""
        static = static.replace("\\", "/")
        obj = self.file_system.find(static)
        if obj is None:
            obj = self.static_files.find(static)

        if obj is not None and isinstance(obj, Static):
            obj.state = FileState.DELETED
            self.write_static()
            self.logger.Custom(f"Removed {obj.relative_url}", clr=WATCHDELETE, label=WATCHLABEL)

    def remove_layout(self, layout: str):
        """Remove a given layout and update all linked pages."""
        layout = layout.replace("\\", "/")
        obj = self.file_system.find(layout)

        if obj is not None and isinstance(obj, Layout):
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(f"Removed {page.relative_url}", clr=WATCHDELETE, label=WATCHLABEL)
            self.file_system.remove(obj.full_path)
            self.file_system.build_hierarchy()
            self.render_pages()

    def remove_page(self, page: str):
        """Remove a given page."""
        page = page.replace("\\", "/")
        obj = self.file_system.find(page)

        if obj is not None and isinstance(obj, Renderable):
            obj.state = FileState.DELETED
            self.render_pages()
            self.logger.Custom(f"Removed {obj.relative_url}", clr=WATCHDELETE, label=WATCHLABEL)

    def remove_component(self, component: str):
        """Remove a given component and update linked pages."""
        component = component.replace("\\", "/")
        obj = self.component_files.find(component)

        if obj is not None and isinstance(obj, Component):
            for page in obj.linked_files:
                page.state = FileState.UPDATED
                self.logger.Custom(f"Removed {page.relative_url}", clr=WATCHDELETE, label=WATCHLABEL)
            self.phml.remove(obj.cname)
            self.render_pages()

class ServerThread(Thread):
    """Thread for the server to allow for serve_forever without interfering with the main thread."""

    def __init__(
        self,
        host: str = "localhost",
        port=PORT_RANGE[0],
        open: bool = False,
        expose_host: bool = False,
        *args, 
        **kwargs
    ):
        super(ServerThread, self).__init__(*args, **kwargs)
        self.server = Server(host, port, open, expose_host)
        
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
        if states["dest"] != "" and directory != states["dest"] and Path(states["dest"]).is_dir():
            directory = Path(states["dest"]).as_posix()
        super().__init__(request, client_address, server, directory=directory)
        self.logger = Log(level=LogLevel.ERROR)

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
    ):

        super().__init__((host, port), ServiceHandler)
        self.open = open
        self.host = host
        self.expose_host = expose_host
        self.is_active = False
        self.logger = Log(level=LogLevel.INFO)
        
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

        # if auto open then open in browser
        if self.open:
            webbrowser.open_new_tab(self.url(self.host))

        # start server
        self.serve_forever()

    def stop(self):
        self._log_stop()
        self.shutdown()
        self.server_close()