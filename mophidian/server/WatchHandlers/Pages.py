from pathlib import PurePath

from log import Log, FColor, color, XTerm
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
    FileSystemEvent,
)


class WatchPages(BaseFileSystemEventHandler):
    def __init__(self, logger: Log):
        super().__init__()
        self._logger = logger
        self.color = FColor.XTERM(XTerm.Grey85)

    def on_closed(self, event: FileClosedEvent):
        '''Called when a file opened for writing is closed.'''

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''Called when a file or directory is created.'''
        self._logger.Custom(
            color("Created", prefix=[FColor.GREEN]),
            f"{PurePath(event.src_path).suffix != ''}, {event.src_path}",
            clr=self.color,
            label="Page",
        )

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''
        self._logger.Custom(
            color("Deleted", prefix=[FColor.RED]),
            f"{PurePath(event.src_path).suffix != ''}, {event.src_path}",
            clr=self.color,
            label="Page",
        )

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        self._logger.Custom(
            color("Modified", prefix=[FColor.YELLOW]),
            f"{PurePath(event.src_path).suffix != ''}, {event.src_path}",
            clr=self.color,
            label="Page",
        )

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        self._logger.Custom(
            color("Moved", prefix=[FColor.CYAN]),
            f"{PurePath(event.src_path).suffix != ''}, {event.src_path}, {event.dest_path}",
            clr=self.color,
            label="Page",
        )
