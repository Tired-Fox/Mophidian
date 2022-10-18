import shutil
import os

from compiler.build import Build
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
                    os.path.normpath('/'.join(['site', event.src_path.split('/', 1)[1]])),
                )
                print(f"Created file {self.replace_prefix('static', 'site', event.src_path)}")
            else:
                shutil.copytree(
                    os.path.normpath(event.src_path),
                    '/'.join(['site', event.src_path.split('/', 1)[1]]),
                )
                print(f"Created directory {self.replace_prefix('static', 'site', event.src_path)}")
        except Exception as e:
            print(e)

    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''
        try:
            if os.path.isfile(self.replace_prefix('static', 'site', event.src_path)):
                self.remove_file(self.replace_prefix('static', 'site', event.src_path))
                print(f"Deleted file {self.replace_prefix('static', 'site', event.src_path)}")
            else:
                try:
                    shutil.rmtree(
                        os.path.normpath('/'.join(['site', event.src_path.split('/', 1)[1]]))
                    )

                    print(
                        f"Deleted directory {self.replace_prefix('static', 'site', event.src_path)}"
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
                print(f"Modified file {self.replace_prefix('static', 'site', event.src_path)}")
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
                print(
                    f"Moved file {self.replace_prefix('static', 'site', event.src_path)} to {self.replace_prefix('static', 'site', event.dest_path)}"
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
                print(
                    f"Moved directory {self.replace_prefix('static', 'site', event.src_path)} to {self.replace_prefix('static', 'site', event.dest_path)}"
                )
        except Exception as e:
            pass
