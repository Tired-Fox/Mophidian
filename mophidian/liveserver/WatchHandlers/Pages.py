from pathlib import Path
import shutil
import os

from compiler.build import Build, Page
from moph_logger import Log, FColor
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
            self.build.add_page(path)

            log_path = (
                f"{Page.build_uri(path)}/index.html"
                if Page.build_uri(path) != "."
                else "/index.html"
            )
            self._logger.Custom(
                f"Created page {log_path}",
                clr=FColor.GREEN,
                label="Pages",
            )
        else:
            Path(self.replace_prefix("pages", "site", event.src_path)).mkdir(
                parents=True, exist_ok=True
            )
            self._logger.Custom(
                f"Created directory {self.replace_prefix('pages', 'site', event.src_path)}",
                clr=FColor.GREEN,
                label="Pages",
            )

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''

        if Path(event.src_path).suffix != "":
            self.build.remove_page(Path(event.src_path))
            dir = 'site/' + Page.build_uri(Path(event.src_path))
            if len(self.folders_in(Path(dir))) > 0:
                self.remove_file(dir + "/index.html")
            else:
                try:
                    shutil.rmtree(os.path.normpath(dir))
                except:
                    pass

            log_path = (
                f"{Page.build_uri(Path(event.src_path))}/index.html"
                if Page.build_uri(Path(event.src_path)) != "."
                else "/index.html"
            )
            self._logger.Custom(
                f"Deleted page {log_path}",
                clr=FColor.RED,
                label="Pages",
            )
        else:
            dir = self.replace_prefix('pages', 'site', event.src_path)
            for path in Path(dir).glob(f"./**/*.html"):
                try:
                    self.build.remove_page(path)
                except:
                    pass

            self._logger.Custom(
                f"Deleted directory {self.replace_prefix('pages', 'site', event.src_path)}",
                clr=FColor.RED,
                label="Pages",
            )

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        try:
            if Path(event.src_path).suffix != "":
                self.build.add_page(Path(event.src_path))

                log_path = (
                    f"{Page.build_uri(Path(event.src_path))}/index.html"
                    if Page.build_uri(Path(event.src_path)) != "."
                    else "/index.html"
                )
                self._logger.Custom(
                    f"Modified page {log_path}",
                    clr=FColor.YELLOW,
                    label="Pages",
                )
        except Exception as e:
            print(e)

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        if Path(event.src_path).suffix != "":
            self.build.remove_page(Path(event.src_path))
            dir = 'site/' + Page.build_uri(Path(event.src_path))
            if len(self.folders_in(Path(dir))) > 0:
                print("Has sub folders")
                self.remove_file(dir + "/index.html")
            else:
                print("Is only file")
                try:
                    shutil.rmtree(os.path.normpath(dir))
                except:
                    pass

            self.build.add_page(Path(event.dest_path))

            log_path = (
                f"{Page.build_uri(Path(event.src_path))}/index.html"
                if Page.build_uri(Path(event.src_path)) != "."
                else "/index.html"
            )

            dlog_path = (
                f"{Page.build_uri(Path(event.dest_path))}/index.html"
                if Page.build_uri(Path(event.dest_path)) != "."
                else "/index.html"
            )

            self._logger.Custom(
                f"Moved page {log_path} to {dlog_path}",
                clr=FColor.CYAN,
                label="Pages",
            )
        else:
            self._logger.Custom(
                f"Moved directory {self.replace_prefix('pages', 'site', event.src_path)} to {self.replace_prefix('pages', 'site', event.dest_path)}",
                clr=FColor.CYAN,
                label="Pages",
            )
