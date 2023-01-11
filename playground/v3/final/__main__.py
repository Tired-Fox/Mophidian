from __future__ import annotations

from FileSystem import build

if __name__ == "__main__":
    files, components, phml = build()
    print(files)
