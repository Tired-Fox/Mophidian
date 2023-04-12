from pathlib import Path
from phml.compiler import scoped_step, add_step
from phml.nodes import Element

from mophidian import CONFIG

ROOT = "/" + CONFIG.site.root.strip("/")

@scoped_step
def replace_at_symbol(node, *_):
    for child in node:
        if isinstance(child, Element):
            attrs = [
                attr
                for attr in ["href", "src", "xlink:href"]
                if attr in child and str(child[attr]).startswith("@/")
            ]
            for attr in attrs:
                new_link = Path(str(child[attr])).as_posix().lstrip("@/")
                child[attr] = f"{ROOT}/{new_link}"

def init_steps():
    add_step(replace_at_symbol, "scoped")
