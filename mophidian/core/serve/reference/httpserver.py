"""
An extreme simple http server
"""
from http import HTTPStatus
from importlib import import_module
import json
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Any

logger = logging.getLogger("of.cli_service")

# Allowed port range for the CLI service
# i.e., a subset of dynamic port range regulated by IANA RFC 6335
# RFC 6335 DPR starts from 49152, we use a larger port to reduce chances of
# collision.
PORT_RANGE = [49200, 65535]
ALLOWED_ORIGINS = ["http://localhost:8081"]

class CliServiceRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_cors_headers()
        BaseHTTPRequestHandler.end_headers(self)

    def send_cors_headers(self):
        origin = self.headers.get("origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)

    def send_json(self, obj: Any):
        self.send_header("Content-Type", "application/json;charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("UTF-8", "replace"))

    def send_text(self, text: str, content_type: str = "text/plain"):
        self.send_header("Content-Type", f"{content_type};charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("UTF-8", "replace"))

    def send_error(self, code: int, message: str = None, explain: str = None):
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = "???", "???"
        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        return self.send_json({"error": message, "explain": explain})

    def handle_request(self) -> None:
        self.send_cors_headers()

        method, path = self.command, self.path
        mod = None
        try:
            mname = f'of.cli_service.routes{path.replace("/", ".")}'.strip(".")
            mod = import_module(mname)
        except ModuleNotFoundError:
            return self.send_error(HTTPStatus.NOT_FOUND)

        handler = mod and getattr(mod, method, None)
        if not handler:
            return self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

        self.send_response(HTTPStatus.ACCEPTED)
        response = handler(self)
        if response:
            if isinstance(response, str):
                self.send_text(response)
            else:
                self.send_json(response)

    def do_HEAD(self):
        self.handle_request()

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()


class CliHttpServer(ThreadingHTTPServer):
    def __init__(self, port=PORT_RANGE[0]):
        super().__init__(("localhost", port), CliServiceRequestHandler)

    def start(self):
        logger.info(f"🚀 CLI service started at http://localhost:{self.server_port}")
        self.serve_forever()

    def stop(self):
        self.shutdown()
        self.server_close()
