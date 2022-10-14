from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime
import os

class BaseFileSystemEventHandler(FileSystemEventHandler):
    def timestamp(self) -> datetime:
        return datetime.utcnow()
    
    def on_any_event(self, event: FileSystemEvent):
        '''Catch-all event handler.'''
        self.last_timestamp = self.timestamp()
        
    def replace_prefix(self, old: str, new: str, path: str) -> str:
        return path.replace(old, new)
    
    def remove_file(self, path: str) -> bool:
        try:
            os.remove(
                os.path.normpath(path)
            )
            return True
        except: 
            return False