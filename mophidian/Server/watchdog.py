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

from mophidian.FileSystem.nodes import Container

class Handler(FileSystemEventHandler):
    file_system: Container
    """The linked file system associated with this handler"""
    
    def __init__(self, file_system: Container) -> None:
        self.file_system = file_system

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
  
        elif event.event_type == 'created':
            # Event is created, you can process it now
            print("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            # Event is modified, you can process it now
            print("Watchdog received modified event - % s." % event.src_path)
    
    def on_modified(self, event):
        return super().on_modified(event)
    
    def on_closed(self, event):
        return super().on_closed(event)
    
    def on_created(self, event):
        return super().on_created(event)
    
    def on_deleted(self, event):
        return super().on_deleted(event)