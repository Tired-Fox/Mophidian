import shutil
import os

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
)


class WatchStatic(BaseFileSystemEventHandler):
    def __init__(self, logger: Log):
        super().__init__()
        self._logger = logger

    def on_closed(self, event: FileClosedEvent):
        '''Called when a file opened for writing is closed.'''
        # print("closed", event, self.__timestamp().strftime('%T.%f')[:-3])

    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''Called when a file or directory is created.'''
        # print("created", event, self.__timestamp().strftime('%T.%f')[:-3])
        try:
            if not event.is_directory:
                shutil.copyfile(
                    os.path.normpath(event.src_path),
                    os.path.normpath(self.replace_prefix('static', 'site', event.src_path)),
                )

                self._logger.Custom(
                    f"Created file {self.replace_prefix('static', 'site', event.src_path)}",
                    clr=FColor.GREEN,
                    label="Static",
                )
            else:
                shutil.copytree(
                    os.path.normpath(event.src_path),
                    '/'.join(['site', event.src_path.split('/', 1)[1]]),
                )
                self._logger.Custom(
                    f"Created directory {self.replace_prefix('static', 'site', event.src_path)}",
                    clr=FColor.GREEN,
                    label="Static",
                )
        except Exception as e:
            print(e)

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''
        try:
            if os.path.isfile(self.replace_prefix('static', 'site', event.src_path)):
                self.remove_file(self.replace_prefix('static', 'site', event.src_path))
                self._logger.Custom(
                    f"Deleted file {self.replace_prefix('static', 'site', event.src_path)}",
                    clr=FColor.RED,
                    label="Static",
                )
            else:
                try:
                    shutil.rmtree(
                        os.path.normpath('/'.join(['site', event.src_path.split('/', 1)[1]]))
                    )

                    self._logger.Custom(
                        f"Deleted directory {self.replace_prefix('static', 'site', event.src_path)}",
                        clr=FColor.RED,
                        label="Static",
                    )
                except:
                    pass
        except Exception as e:
            pass

    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        try:
            if not event.is_directory:
                self.remove_file(self.replace_prefix('static', 'site', event.src_path))
                shutil.copyfile(
                    os.path.normpath(event.src_path),
                    os.path.normpath('/'.join(['site', event.src_path.split('/', 1)[1]])),
                )
                self._logger.Custom(
                    f"Modified file {self.replace_prefix('static', 'site', event.src_path)}",
                    clr=FColor.MAGENTA,
                    label="Static",
                )
        except Exception as e:
            pass

    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        # print("moved", event, self.__timestamp().strftime('%T.%f')[:-3])
        try:
            if not event.is_directory:
                self.remove_file(self.replace_prefix('static', 'site', event.src_path))
                shutil.copyfile(
                    os.path.normpath(event.dest_path),
                    os.path.normpath(self.replace_prefix('static', 'site', event.dest_path)),
                )

                self._logger.Custom(
                    f"Moved file {self.replace_prefix('static', 'site', event.src_path)} to {self.replace_prefix('static', 'site', event.dest_path)}",
                    clr=FColor.CYAN,
                    label="Static",
                )
            else:
                try:
                    print(
                        shutil.rmtree(
                            os.path.normpath('/'.join(['site', event.src_path.split('/', 1)[1]]))
                        )
                    )
                except:
                    pass
                shutil.copytree(
                    os.path.normpath(event.dest_path),
                    '/'.join(['site', event.dest_path.split('/', 1)[1]]),
                )

                self._logger.Custom(
                    f"Moved directory {self.replace_prefix('static', 'site', event.src_path)} to {self.replace_prefix('static', 'site', event.dest_path)}",
                    clr=FColor.CYAN,
                    label="Static",
                )
        except Exception as e:
            pass
