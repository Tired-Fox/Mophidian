from pathlib import Path
from phml import PHML
import re
import posixpath

layout_re = re.compile(r"layout(@[a-zA-Z0-9]+)?\.phml")
page_re = re.compile(r"page(@[a-zA-Z0-9()]+)?\.phml")

group_re = re.compile(r"\([a-zA-Z0-9]+\)")
group_seg_re = re.compile(r"\/\([a-zA-Z0-9]+\)\/")
group_seg_lead_re = re.compile(r"\([a-zA-Z0-9]+\)\/")
file_name_re = re.compile(r"(page|layout)@?([a-zA-Z0-9]+)?(.phml)")
layouts = {}

root = "files/"
out_dir = "out/"

phml = PHML()


class Node:
    def __init__(self, path: str) -> None:
        self.path = path

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, self.__class__) and __o.path == self.path

    def print(self, depth: 0) -> str:
        out = (
            f"{' ' * depth}\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.path!r}\x1b[0m"
        )
        if hasattr(self, "children"):
            for child in self.children:
                out += "\n" + child.print(depth + 4)
        return out

    def __str__(self) -> str:
        out = f"\x1b[34m{self.__class__.__name__}\x1b[0m > \x1b[32m{self.path!r}\x1b[0m"
        if hasattr(self, "children"):
            for child in self.children:
                out += "\n" + child.print(4)
        return out


class File(Node):
    def __init__(self, path: str) -> None:
        super().__init__(path)

        # Dest path
        self.dest = path
        while True:
            if group_seg_re.match(self.dest) is not None:
                self.dest = group_seg_re.sub("/", self.dest)
            elif group_seg_lead_re.match(self.dest) is not None:
                self.dest = group_seg_lead_re.sub("", self.dest)
            else:
                break
        self.dest = Path("/".join(self.dest.split("/")[:-1])).joinpath("index.html").as_posix()

        # file name
        file_info = file_name_re.search(path)
        self.file_name, self.inherits, self.extension = (
            file_info.groups() if file_info is not None else ("", None, "")
        )

        # self.file_name = Path(path).name.replace(Path(path).suffix, "")
        self.inherits = None

        # url


class Layout(File):
    pass


class Page(File):
    pass


class Group(Node):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.children = []


class Directory(Node):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.children = []


layout_root = Directory("")
page_root = Directory("")


def add_file(file, path: list[str], root):
    current = root
    for i, segment in enumerate(path):
        if i > 0:
            if Path('/'.join(path[: i + 1])).is_file():
                current.children.append(file)
            elif group_re.match(segment) is not None:
                found = False
                for group in [child for child in current.children if isinstance(child, Group)]:
                    if group.path == '/'.join(path[1 : i + 1]):
                        current = group
                        found = True
                        break

                if not found:
                    new = Group('/'.join(path[1 : i + 1]))
                    current.children.append(new)
                    current = new
            else:
                found = False
                for directory in [
                    child for child in current.children if isinstance(child, Directory)
                ]:
                    if directory.path == '/'.join(path[1 : i + 1]):
                        current = directory
                        found = True
                        break

                if not found:
                    new = Directory('/'.join(path[1 : i + 1]))
                    current.children.append(new)
                    current = new

    return current


if __name__ == "__main__":
    for phml_page in Path("files").glob("**/*.phml"):
        if layout_re.match(phml_page.name) is not None:
            path = phml_page.as_posix().split('/')
            add_file(Layout('/'.join(path[1:])), path, layout_root)

        elif page_re.match(phml_page.name) is not None:
            path = phml_page.as_posix().split('/')
            add_file(Page('/'.join(path[1:])), path, page_root)

    print(layout_root, end="\n\n\n")
    print(page_root)
