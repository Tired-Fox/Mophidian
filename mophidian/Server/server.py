from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import socket
from pathlib import Path
import posixpath
from threading import Thread
from typing import Any
import webbrowser

from teddecor import TED, Logger, style, Log, LogLevel

from mophidian import states, CONFIG, DestState
from mophidian.FileSystem import render_pages, write_static_files
from mophidian.FileSystem.nodes import Container, File, Renderable

PORT_RANGE = [49200, 65535]

# Reference: https://docs.python.org/3/library/http.server.html

hostName = "localhost"
serverPort = 8080

# TODO: Use watch dog and watch for changes, if any occur stop the server and start again

class LiveServer:
    def __init__(
        self,
        host: str = "localhost",
        port=PORT_RANGE[0],
        open: bool = False,
        expose_host: bool = False,
    ) -> None:
        self._server = Server(host, port, open, expose_host)
        # TODO: Construct watchdog instance
        self._watchdog = None

    def _update(self, full_path: str):
        """Set the state of a given file to updated.

        Args:
            full_path (str): full path of the source file to set as updated.
                This file will be removed on the next render loop.
        """
        # TODO: find file in file structure and set to FileState.UPDATED

    def _delete(self, full_path: str):
        """Set the state of a given file to deleted.

        Args:
            full_path (str): full path of the source file to set as deleted.
                This file will be removed on the next render loop.
        """
        # TODO: find file in file structure and set to FileState.DELETED

    def _create(self, full_path: str):
        """Add a file to the file_system.

        Args:
            full_path (str): full path of the file to add to the file system.
                This file will be rendered on the next render loop.
        """
        # TODO: Create new file based on full_path conditions and add to file_system

    def start(
        self,
        file_system: Container,
        static: Container,
        components: Container,
        phml: Container
    ):
        # TODO: Start Server in it's own thread
        # TODO: Start 
        pass

class ServerThread(Thread):
    """Thread for the server to allow for serve_forever without interfering with the main thread."""

    def __init__(self, server: Server, *args, **kwargs):
        super(ServerThread, self).__init__(*args, **kwargs)
        self.server = server
        self.once = False

    def run(self) -> None:
        if not self.once:
            self.server.start()
            self.once = True
        else:
            self.server.serve_forever()

    def stop(self, final: bool = False):
        if final:
            self.server.stop()
        else:
            self.server.shutdown()

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
        return super().shutdown()
    
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
        self.logger.Custom(
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