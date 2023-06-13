from __future__ import annotations

from mophidian import Compiler, fsprint

compiler = Compiler()

fsprint(compiler.file_system)
print()
fsprint(compiler.public)
print()
fsprint(compiler.components)
print()
fsprint(compiler.scripts)
