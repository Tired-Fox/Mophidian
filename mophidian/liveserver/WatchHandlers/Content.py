from pathlib import Path
import shutil
import os
from datetime import datetime
from typing import TextIO

from compiler.build import Build, Page
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
    def __init__(self, build: Build, stdout: TextIO):
        super().__init__()
        self.build = build
        self.stdout = stdout

    def on_closed(self, event: FileClosedEvent):
        '''Called when a file opened for writing is closed.'''
        print("closed", event, self.timestamp().strftime('%T.%f')[:-3])

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''Called when a file or directory is created.'''
        if not event.is_directory:
            path = Path(event.src_path)
            self.build.add_content(path)
            print(f"Created file {self.replace_prefix('content', 'site', event.src_path)}")
        else:
            Path(self.replace_prefix("content", "site", event.src_path)).mkdir(
                parents=True, exist_ok=True
            )
            print(f"Created directory {self.replace_prefix('content', 'site', event.src_path)}")

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''

        if Path(event.src_path).suffix != "":
            self.build.remove_content(Path(event.src_path))
            dir = 'site/' + Page.build_uri(Path(event.src_path))
            if len(self.folders_in(Path(dir))) > 0:
                self.remove_file(dir + "/index.html")
            else:
                try:
                    shutil.rmtree(os.path.normpath(dir))
                except:
                    pass
            print(f"Deleted file {self.replace_prefix('content', 'site', event.src_path)}")
        else:
            dir = self.replace_prefix('content', 'site', event.src_path)
            for path in Path(dir).glob(f"./**/*.html"):
                try:
                    self.build.remove_content(path)
                except:
                    pass

            self.build.full()
            print(f"Deleted directory {self.replace_prefix('content', 'site', event.src_path)}")

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        try:
            if Path(event.src_path).suffix != "":
                self.build.add_content(Path(event.src_path))
                print(f"Modified file {self.replace_prefix('content', 'site', event.src_path)}")
        except Exception as e:
            print(e)

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        if Path(event.src_path).suffix != "":
            self.build.remove_content(Path(event.src_path))
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

            self.build.add_content(Path(event.dest_path))

            print(
                f"Moved file {self.replace_prefix('content', 'site', event.src_path)} to {self.replace_prefix('content', 'site', event.dest_path)}"
            )
        else:
            print(
                f"Moved directory {self.replace_prefix('content', 'site', event.src_path)} to {self.replace_prefix('content', 'site', event.dest_path)}"
            )
