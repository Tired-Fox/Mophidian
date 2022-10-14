import shutil
import os
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
    DirMovedEvent
)

class WatchPages(BaseFileSystemEventHandler):    
    def on_closed(self, event: FileClosedEvent):
        '''Called when a file opened for writing is closed.'''
        print("closed", event, self.__timestamp().strftime('%T.%f')[:-3])
    
    def on_created(self, event: FileCreatedEvent | DirCreatedEvent):
        '''Called when a file or directory is created.'''
        print("created", event, self.__timestamp().strftime('%T.%f')[:-3])
    
    def on_deleted(self, event: FileDeletedEvent | DirDeletedEvent):
        '''Called when a file or directory is deleted.'''
        print("deleted", event, self.__timestamp().strftime('%T.%f')[:-3])
    
    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        '''Called when a file or directory is modified.'''
        print("modified", event, self.__timestamp().strftime('%T.%f')[:-3])
    
    def on_moved(self, event: FileMovedEvent | DirMovedEvent):
        '''Called when a file or a directory is moved or renamed.'''
        print("moved", event, self.__timestamp().strftime('%T.%f')[:-3])