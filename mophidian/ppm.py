from __future__ import annotations


from os import system
from shutil import which
import subprocess


class PPM:
    ppm: NPM | Yarn | PNPM
    """The preferred package manager currently selected."""

    types: list[type]
    """All the current types of package managers that can be chosen."""

    names: list[str]
    """List of the valid package manager names"""

    def __init__(self, ppm_: str = "npm"):
        self.types: list[type] = [self.NPM, self.PNPM, self.Yarn]
        self.names: list[str] = [t.name() for t in self.types]
        self.ppm = self.get(ppm_)

    def is_valid(self, ppm_: str) -> bool:
        from shutil import which

        if ppm_ in self.names:
            if which(ppm_) is not None:
                self.ppm = self.types[self.names.index(ppm_)]()
                return True
            return False
        else:
            return False

    def get(self, ppm_: str) -> NPM | Yarn | PNPM:
        from shutil import which

        if ppm_ in self.names:
            if which(ppm_) is not None:
                return self.types[self.names.index(ppm_)]()
        return self.types[self.names.index(self.NPM.name())]()

    class NPM:
        def __inti__(self):
            self._init = "npm init"
            self._run = "npm run"

        @classmethod
        def name(cls) -> str:
            return cls.__name__.lower()

        @classmethod
        def new(cls):
            return cls()

        def init(self):
            """Run the init command associated with the package manager."""
            system(self._init)

        def install(self, package: str, *args: str) -> str:
            """Builds the install/add command for a given package.

            Args:
                package (str): The package that will be installed
            """
            cmd = f"npm i {' '.join(args)} {package}"
            print(cmd)
            system(cmd)

        def run(self, command: str):
            """Run a command from the package.json using the notation from this package manager."""
            cmd = f"{self._run} {command}"
            system(cmd)

        def run_command(self, command: str) -> str:
            """Get the built run command for this node package manager"""
            return f"{self._run.replace(self.name(), str(which(self.name())))} {command}"

    class Yarn(NPM):
        def __init__(self):
            self._init = "yarn init"
            self._run = "yarn"

        def install(self, package: str, *args: str):
            """Builds the install/add command for a given package.

            Args:
                package (str): The package that will be installed
            """
            cmd = f"yarn add {' '.join(args)} {package}"
            print(cmd)
            system(cmd)

    class PNPM(NPM):
        def __init__(self):
            self._init = "npm init"
            self._run = "pnpm"

        def install(self, package: str, *args: str):
            """Builds the install/add command for a given package.

            Args:
                package (str): The package that will be installed
            """
            cmd = f"pnpm add {' '.join(args)} {package}"
            print(cmd)
            system(cmd)
