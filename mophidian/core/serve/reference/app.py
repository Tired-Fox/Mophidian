import importlib
import importlib.util
import logging
import sys
import threading
import time
from threading import Thread
from typing import Set

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from . import httpserver
from .utils import file_path_to_module_name, is_port_in_use, root_path


logger = logging.getLogger("of.cli_service")
logger.handlers = [logging.StreamHandler()]


def start_server_thread(port: int):
    """Start the CLI http server in another thread"""
    try:
        importlib.reload(httpserver)  # always reload the module
    except SyntaxError:
        # ignore syntax error (which often means we are editting files)
        logger.exception("Reloading httpserver module failed")
        return
    server = httpserver.CliHttpServer(port)
    server_thread = Thread(target=lambda: server.start())
    server_thread.start()
    return server


class AutoreloadHandler(PatternMatchingEventHandler):
    """Auto reload handlers"""

    def __init__(
        self,
        server: httpserver.CliHttpServer,
        patterns=None,
        ignore_patterns=None,
        ignore_directories=False,
        case_sensitive=False,
    ):
        super().__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
        self.server = server
        self.needs_reload: Set[str] = set()  # modules that need to be reloaded

        # mark last update to make sure we only reload 1s after the last update

        self.last_updated_at = time.time()
        # start another thread to check if we need to reload
        threading.Thread(target=lambda: self.check_reload()).start()

    def reload_modules(self):
        logging.debug("%s modules updated", len(self.needs_reload))
        for mname in self.needs_reload:
            logging.debug(mname)
            if mname in sys.modules:
                importlib.reload(sys.modules[mname])
        self.needs_reload.clear()

    def check_reload(self):
        while True:
            if self.needs_reload and time.time() - self.last_updated_at > 1:
                logger.debug("Change detected, restarting CLI service...\n")
                self.reload_modules()
                self.server.stop()
                new_server = start_server_thread(self.server.server_port)
                if new_server:
                    self.server = new_server
            time.sleep(1)

    def on_any_event(self, event):
        self.needs_reload.add(file_path_to_module_name(event.src_path))
        self.last_updated_at = time.time()


def start_cli_service(autoreload=True):
    """Find available private (dynamic) port for the CLI service and start
    the service."""
    port, max_port = httpserver.PORT_RANGE
    while port < max_port and is_port_in_use(port):
        port += 1

    server = start_server_thread(port)
    observer = None

    if autoreload:
        # start autoreload watcher in another thread
        observer = Observer()
        observer.schedule(
            AutoreloadHandler(
                server=server,
                patterns=["*.py"],
                ignore_patterns=["__pycache__", "cli_service/app.py"],
            ),
            # monitor all "of.xxx" files
            root_path,
            recursive=True,
        )
        observer.start()
        observer.on_thread_stop = lambda: server.stop()

    return port, observer
