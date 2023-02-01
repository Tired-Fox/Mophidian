from inspect import signature
from pathlib import Path
from threading import Timer
import time
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileSystemEvent,
    FileClosedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemMovedEvent
)

from mophidian import CONFIG
from mophidian.FileSystem import REGEX

observer = Observer()
Callbacks = dict[str, dict[str, Callable]]

def debounce(wait):
    def decorator(fn):
        sig = signature(fn)
        caller = {}

        def debounced(*args, **kwargs):
            nonlocal caller

            try:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                called_args = fn.__name__ + str(dict(bound_args.arguments))
            except:
                called_args = ''

            t_ = time.time()

            def call_it(key):
                try:
                    # always remove on call
                    caller.pop(key)
                except:
                    pass

                fn(*args, **kwargs)

            try:
                # Always try to cancel timer
                caller[called_args].cancel()
            except:
                pass

            caller[called_args] = Timer(wait, call_it, [called_args])
            caller[called_args].start()

        return debounced

    return decorator
    
WAIT = 0.1
    
class Handler(FileSystemEventHandler):
    def __init__(self, callbacks: Callbacks) -> None:
        self._callbacks = callbacks

    @debounce(WAIT)
    def on_any_event(self, event):
        pass
    
    def is_static(self, path) -> bool:
        pPath = Path(path)
        return bool(pPath.suffix not in [".phml", ".md", ".mdx"])

    def is_layout(self, path) -> bool:
        pPath = Path(path)
        return bool(
            path.startswith(CONFIG.site.source.strip("/"))
            and pPath.suffix == ".phml"
            and REGEX["layout"]["name"].match(pPath.name) is not None
        )

    def is_page(self, path) -> bool:
        pPath = Path(path)
        return bool(
            path.startswith(CONFIG.site.source.strip("/"))
            and pPath.suffix == ".phml"
            and REGEX["page"]["name"].match(pPath.name) is not None
        )

    def is_component(self, path) -> bool:
        pPath = Path(path)
        return bool(
            path.startswith(CONFIG.site.components.strip("/"))
            and pPath.suffix == ".phml"
        )

    @debounce(WAIT)
    def on_modified(self, event):
        path = event.src_path
        if self.is_static(path):
            self._callbacks["update"]["static"](path)
        elif self.is_page(path):
            self._callbacks["update"]["page"](path)
        elif self.is_layout(path):
            self._callbacks["update"]["layout"](path)
        elif self.is_component(path):
            self._callbacks["update"]["component"](path)

    @debounce(WAIT)
    def on_closed(self, event):
        print("Close Event")

    @debounce(WAIT)
    def on_created(self, event):
        path = event.src_path
        if self.is_static(path):
            self._callbacks["create"]["static"](path)
        elif self.is_page(path):
            self._callbacks["create"]["page"](path)
        elif self.is_layout(path):
            self._callbacks["create"]["layout"](path)
        elif self.is_component(path):
            self._callbacks["create"]["component"](path)

    @debounce(WAIT)
    def on_deleted(self, event):
        path = event.src_path
        if self.is_static(path):
            self._callbacks["remove"]["static"](path)
        elif self.is_page(path):
            self._callbacks["remove"]["page"](path)
        elif self.is_layout(path):
            self._callbacks["remove"]["layout"](path)
        elif self.is_component(path):
            self._callbacks["remove"]["component"](path)
