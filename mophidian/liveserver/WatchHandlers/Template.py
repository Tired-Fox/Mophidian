import shutil
import os

from moph_logger import Log, FColor
from compiler.build import Build
from pathlib import Path
from .BaseHandler import BaseFileSystemEventHandler
from watchdog.events import (
    FileClosedEvent,
    FileCreatedEvent,
    DirCreatedEvent,
    FileModifiedEvent,
    DirModifiedEvent,
    FileDeletedEvent,
    DirDeletedEvent,
    FileMovedEvent,
    DirMovedEvent,
)


class WatchTemplates(BaseFileSystemEventHandler):
    def __init__(self, build: Build, logger: Log):
        super().__init__()
        self._logger = logger
        self._build = build

    def on_closed(self, event: FileClosedEvent):
        '''Called when a file opened for writing is closed.'''

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''Called when a file or directory is created.'''
        path = Path(event.src_path)

        if path.suffix != "":
            root = path.parent.as_posix().split("/", 1)[0]
            if root == "components":
                self._build.add_component(path)
            elif root == "layouts":
                self._build.add_layout(path)

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''
        path = Path(event.src_path)

        root = path.parent.as_posix().split("/", 1)[0]
        if root == "components":
            self._build.remove_component(path)
        elif root == "layouts":
            self._build.remove_component(path)

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        path = Path(event.src_path)

        if path.suffix != "":
            root = path.parent.as_posix().split("/", 1)[0]
            if root == "components":
                self._build.add_component(path)
            elif root == "layouts":
                self._build.add_layout(path)

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        '''Called when a file or a directory is moved or renamed.'''
        path = Path(event.src_path)
        if path.suffix != "":
            root = path.parent.as_posix().split("/", 1)[0]
            if root == "components":
                self._build.remove_component(path)
                self._build.add_component(Path(event.dest_path))
            elif root == "layouts":
                self._build.remove_layout(path)
                self._build.add_layout(Path(event.dest_path))
