from pathlib import Path, PurePath
from phml import PHML
import re

from util import get_group_name, first

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
        input(f"{self.path} | {self.inherits}")
        # self.file_name = Path(path).name.replace(Path(path).suffix, "")

        # url


class Layout(File):
    def __init__(self, path: str) -> None:
        self.parent = None
        super().__init__(path)
        
    def __str__(self) -> str:
        return f"Layout({self.path!r}, parent={self.parent}, inherits={self.inherits!r})"
    def __repr__(self) -> str:
        return f"Layout({self.path!r}, parent={self.parent}, inherits={self.inherits!r})"


class Page(File):
    pass


class Container(Node):
    def __init__(self, path: str, name: str) -> None:
        super().__init__(path)
        self.children = []
        self.name = name

    def find_layout_by_name(self, name: str) -> Layout | None:
        """Name of the layout, either by layout name or group name.

        Example:
            layout name: layout@account.phml
            group name: (account)/layout.phml

        Args:
            name (str): Name of the layout to find. Either name of the layout or the group name
                where the layout is located.

        Returns:
            Layout | None: A layout if found otherwise None.
        """
        for child in self.children:
            if isinstance(child, Group) and child.name == name:
                result = first(
                    lambda l: isinstance(l, Layout) and l.inherits is None, child.children
                )
                if result is not None:
                    return result

            if isinstance(child, Layout):
                if child.inherits == name:
                    return child
        return None

    def find_page(self) -> Layout:
        """Find page by destination path or url which are the same +/- index.html."""
        return Layout("")


class Group(Container):
    def __init__(self, path: str) -> None:
        super().__init__(path, get_group_name(path.split("/")[-1]))


class Directory(Container):
    def __init__(self, path: str) -> None:
        super().__init__(path, path.split("/")[-1])


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

def add_layout_parents(layout_root: Directory):
    def iterate_children(current: Directory | Group, parent: Layout | None = None):
        layouts = [layout for layout in current.children if isinstance(layout, Layout) and layout.inherits is None]
        input(layouts)
        containers = [cont for cont in current.children if isinstance(cont, (Directory, Group))]
        if len(layouts) > 1:
            raise Exception(f"More than one layout for directory or group: {current.path}")
        
        layout = parent
        if len(layouts) == 1:
            layout = layouts[0]
            layout.parent = parent
            
        
        for container in containers:
            iterate_children(container, layout)
    
    iterate_children(layout_root)


if __name__ == "__main__":
    for phml_page in Path("files").glob("**/*.phml"):
        if layout_re.match(phml_page.name) is not None:
            path = phml_page.as_posix().split('/')
            add_file(Layout('/'.join(path[1:])), path, layout_root)

        elif page_re.match(phml_page.name) is not None:
            path = phml_page.as_posix().split('/')
            add_file(Page('/'.join(path[1:])), path, page_root)

    add_layout_parents(layout_root)
    print(layout_root, end="\n\n\n")
    print(layout_root.find_layout_by_name("blog"))
