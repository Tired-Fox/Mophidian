from __future__ import annotations

from pathlib import Path
from phml import PHML

from FileSystem import REGEX, Directory, Page, Layout, Component

out_dir = "out/"


if __name__ == "__main__":
    phml = PHML()
    root = Directory("files/")
    components = Directory("components/")

    for file in Path(components.path).glob("**/*.*"):
        if file.suffix == ".phml":
            components.add(Component(file.as_posix()))

    for file in components.files():
        phml.add(file.full_path, strip_root=True)

    print(components, end="\n\n")

    for file in Path(root.path).glob("**/*.*"):
        if file.suffix == ".phml":
            if REGEX["layout"]["name"].match(file.name) is not None:
                root.add(Layout(file.as_posix()))
            elif REGEX["page"]["name"].match(file.name) is not None:
                root.add(Page(file.as_posix()))

    root.build_hierarchy()

    print(root, end="\n\n")

    for page in root.pages():
        page.dest(out_dir).parent.mkdir(parents=True, exist_ok=True)
        with open(page.dest(out_dir), "+w", encoding="utf-8") as file:
            file.write(page.render(phml, title="Sample"))
