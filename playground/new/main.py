from __future__ import annotations
from shutil import rmtree

from mophidian import Compiler, fsprint
from mophidian.config import CONFIG

if __name__ == "__main__":
    rmtree(CONFIG.paths.out)
    compiler = Compiler()
    
    fsprint(compiler.file_system)
    print()
    fsprint(compiler.public)
    print()
    fsprint(compiler.components)
    print()
    fsprint(compiler.scripts)

    compiler.build()

    callout = compiler.components.by_context("cname", "Callout")
    if callout is not None:
        print(callout.linked)
