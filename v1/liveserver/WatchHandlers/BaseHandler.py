from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from datetime import datetime
import os


class BaseFileSystemEventHandler(FileSystemEventHandler):
    def timestamp(self) -> datetime:
        return datetime.utcnow()

    def folders_in(self, parent: Path) -> list[str]:
        path = str(parent)
        folders = []
        for fname in os.listdir(path):
            if os.path.isdir(os.path.join(path, fname)):
                folders.append(os.path.join(path, fname))

        return folders

    def replace_prefix(self, old: str, new: str, path: str) -> str:
        return path.replace(old, new)

    def remove_file(self, path: str) -> bool:
        try:
            os.remove(os.path.normpath(path))
            return True
        except:
            return False
