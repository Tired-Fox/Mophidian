from pathlib import Path
import sys

sys.path.append(Path(__file__).parent.parent.as_posix())

from new.fs import Directory, fsprint, FileType, layouts, FileSystem
from phml import HypertextManager

if __name__ == "__main__":
    phml = HypertextManager()

    temp = Path("pages/temp.phml").write_text("", "utf-8")
    fs = FileSystem("pages").glob("**/*")

    components = FileSystem("components").glob("**/*.phml")
    for component in components.walk(FileType.File):
        phml.add(component.path, ignore=component.ignore)

    fsprint(fs)
    print(fs["blog/"])

    fs["temp.phml"].delete()
    fsprint(fs)

