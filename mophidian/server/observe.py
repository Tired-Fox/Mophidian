from pathlib import Path
import threading
from watchdog.observers import Observer

from .WatchHandlers import WatchContent, WatchPages, WatchStatic, WatchTemplates
from log import Log, LL

all = ["WatchFiles"]


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super().__init__(daemon=True, *args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class WatchFiles(StoppableThread):
    def __init__(self, logger: Log):
        super().__init__()

        # Allow for custom watched dirs
        self._logger = logger

    def run(self):
        # Init file event handlers
        content_event_handler = WatchContent(logger=self._logger)
        page_event_handler = WatchPages(logger=self._logger)
        static_event_handler = WatchStatic(logger=self._logger)
        template_event_handler = WatchTemplates(logger=self._logger)

        # Create observer and schedule to observe content and pages
        observer = Observer()

        if Path("content/").exists():
            observer.schedule(content_event_handler, "content/", recursive=True)

        if Path("pages/").exists():
            observer.schedule(page_event_handler, "pages/", recursive=True)

        if Path("static/").exists():
            observer.schedule(static_event_handler, 'static/', recursive=True)

        if Path("components/").exists():
            observer.schedule(template_event_handler, "components/", recursive=True)

        if Path("layouts/").exists():
            observer.schedule(template_event_handler, "layouts/", recursive=True)

        # Start observing files
        observer.start()
        while observer.is_alive() and not self.stopped():
            observer.join(1)

        # Stop observing files
        observer.stop()
        observer.join()
