from enum import Enum
from typing import Protocol, runtime_checkable

@runtime_checkable
class FS(Protocol):
    def __fstr__(self, indent: int = 0) -> str:
        ...


def fsprint(fs: FS):
    if isinstance(fs, FS):
        print(fs.__fstr__())
    else:
        raise TypeError(f"Invalid file system object: {fs}")


class FileType(Enum):
    All = 0
    File = 1

    Markdown = 2
    Layout = 3
    Page = 4
    Static = 5

    Directory = 5
    Group = 7

    # PERF: WIP: Just ideas
    # Catch = 7
    # CatchAll = 8

class FileState(Enum):
    NC = 0
    Deleted = 1
    Created = 2
    Modified = 3
