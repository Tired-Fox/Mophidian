from pathlib import Path
import shutil
import os
from datetime import datetime
from typing import TextIO

from compiler.build import Build, Page
from moph_logger import Log, FColor, color
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


class WatchContent(BaseFileSystemEventHandler):
    def __init__(self, build: Build, logger: Log):
        super().__init__()
        self.build = build
        self._logger = logger

    def on_closed(self, event: FileClosedEvent):
        '''Called when a file opened for writing is closed.'''
        print("closed", event, self.timestamp().strftime('%T.%f')[:-3])

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''Called when a file or directory is created.'''
        if not event.is_directory:
            path = Path(event.src_path)
            self.build.add_content(path)

            log_path = (
                f"{Page.build_uri(path)}/index.html"
                if Page.build_uri(path) != "."
                else "/index.html"
            )
            self._logger.Custom(
                color("Created", prefix=[FColor.GREEN]),
                f"page {log_path}",
                label="Content",
            )
        else:
            Path(self.replace_prefix("content", "site", event.src_path)).mkdir(
                parents=True, exist_ok=True
            )
            self._logger.Custom(
                f"Created directory {self.replace_prefix('content', 'site', event.src_path)}",
                clr=FColor.GREEN,
                label="Content",
            )

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''

        if Path(event.src_path).suffix != "":
            path = Path(event.src_path)

            self.build.remove_content(path)
            dir = 'site/' + Page.build_uri(path)
            if len(self.folders_in(Path(dir))) > 0:
                self.remove_file(dir + "/index.html")
            else:
                try:
                    shutil.rmtree(os.path.normpath(dir))
                except:
                    pass

            log_path = (
                f"{Page.build_uri(path)}/index.html"
                if Page.build_uri(path) != "."
                else "/index.html"
            )
            self._logger.Custom(
                color("Deleted", prefix=[FColor.RED]),
                f"page {log_path}",
                label="Content",
            )
        else:
            dir = self.replace_prefix('content', 'site', event.src_path)
            for path in Path(dir).glob(f"./**/*.html"):
                try:
                    self.build.remove_content(path)
                except:
                    pass

            self._logger.Custom(
                color("Deleted", prefix=[FColor.RED]),
                f"directory {self.replace_prefix('content', 'site', event.src_path)}",
                label="Content",
            )

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        try:
            path = Path(event.src_path)

            if path.suffix != "":
                self.build.add_content(path)

                log_path = (
                    f"{Page.build_uri(path)}/index.html"
                    if Page.build_uri(path) != "."
                    else "/index.html"
                )
                self._logger.Custom(
                    color("Modified", prefix=[FColor.YELLOW]),
                    f"page {log_path}",
                    label="Content",
                )
        except Exception as e:
            print(e)

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        if Path(event.src_path).suffix != "":
            path = Path(event.src_path)
            dpath = Path(event.dest_path)

            self.build.remove_content(path)
            dir = 'site/' + Page.build_uri(path)
            if len(self.folders_in(Path(dir))) > 0:
                print("Has sub folders")
                self.remove_file(dir + "/index.html")
            else:
                print("Is only file")
                try:
                    shutil.rmtree(os.path.normpath(dir))
                except:
                    pass

            self.build.add_content(dpath)

            log_path = (
                f"{Page.build_uri(path)}/index.html"
                if Page.build_uri(path) != "."
                else "/index.html"
            )

            dlog_path = (
                f"{Page.build_uri(dpath)}/index.html"
                if Page.build_uri(dpath) != "."
                else "/index.html"
            )
            self._logger.Custom(
                color("Moved", prefix=[FColor.CYAN]),
                f"file {log_path} to {dlog_path}",
                label="Content",
            )
        else:
            self._logger.Custom(
                color("Moved", prefix=[FColor.CYAN]),
                f"directory {self.replace_prefix('content', 'site', event.src_path)} to {self.replace_prefix('content', 'site', event.dest_path)}",
                label="Content",
            )
