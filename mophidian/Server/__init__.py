from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import socket
from pathlib import Path
import posixpath
from typing import Any
import webbrowser

from teddecor import TED, Logger, style

from mophidian import states, CONFIG, DestState

PORT_RANGE = [49200, 65535]

# Reference: https://docs.python.org/3/library/http.server.html

hostName = "localhost"
serverPort = 8080

# TODO: Use watch dog and watch for changes, if any occur stop the server and start again

class ServiceHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server, *, directory: str | None = "") -> None:
        if states["dest"] != "" and directory != states["dest"] and Path(states["dest"]).is_dir():
            directory = Path(states["dest"]).as_posix()
        super().__init__(request, client_address, server, directory=directory)

    def log_request(self, code: int | str = ..., size: int | str = ...) -> None:
        # TODO: Custom request messages
        pass

    def log_error(self, format: str, *args: Any) -> None:
        # TODO: Custom error messages
        pass

class Server(ThreadingHTTPServer):
    def __init__(self, host: str = "localhost", port=PORT_RANGE[0], open: bool = False, expose_host: bool = False):
        super().__init__((host, port), ServiceHandler)
        self.open = open
        self.host = host
        self.expose_host = expose_host

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
            Logger.custom(
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

    def start(self):
        # Log the url of the server
        self._log_start()

        # if auto open then open in browser
        if self.open:
            webbrowser.open_new_tab(self.url(self.host))

        # start server
        self.serve_forever()

    def stop(self):
        self.shutdown()
        self.server_close()
        
class LiveServer(ThreadingHTTPServer):
    def __init__(self, host: str = "localhost", port=PORT_RANGE[0], open: bool = False, expose_host: bool = False):
        super().__init__((host, port), ServiceHandler)
        self.open = open
        self.host = host
        self.expose_host = expose_host

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
            Logger.custom(
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

    def start(self):
        # Log the url of the server
        self._log_start()

        # if auto open then open in browser
        if self.open:
            webbrowser.open_new_tab(self.url(self.host))

        # start server
        self.serve_forever()

    def stop(self):
        self.shutdown()
        self.server_close()