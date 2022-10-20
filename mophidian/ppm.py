from __future__ import annotations
from io import TextIOWrapper


from os import system
from shutil import which
import sys
from typing import TextIO

from moph_logger import Log, LL, FColor


class PPM:
    ppm: NPM | Yarn | PNPM
    """The preferred package manager currently selected."""

    types: list[type]
    """All the current types of package managers that can be chosen."""

    names: list[str]
    """List of the valid package manager names"""

    def __init__(self, ppm_: str = "npm", logger: Log = Log()):
        self.types: list[type] = [NPM, PNPM, Yarn]
        self.names: list[str] = [t.name() for t in self.types]
        self._logger = logger
        self.ppm = self.get(ppm_)

    def is_valid(self, ppm_: str) -> bool:
        from shutil import which

        if ppm_ in self.names:
            if which(ppm_) is not None:
                self.ppm = self.types[self.names.index(ppm_)](self._logger)
                return True
            return False
        else:
            return False

    def get(self, ppm_: str) -> NPM | Yarn | PNPM:
        from shutil import which

        if ppm_ in self.names:
            if which(ppm_) is not None:
                return self.types[self.names.index(ppm_)](logger=self._logger)
        return self.types[self.names.index(NPM.name())](logger=self._logger)


class NPM:
    def __init__(
        self, logger: Log, init: str = "npm init", install: str = "npm i", run: str = "npm run"
    ):
        self._init = init
        self._install = install
        self._run = run
        self._logger = logger

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    def init(self):
        """Run the init command associated with the package manager."""
        self._logger.Custom(self._init, label=self.name().upper())
        system(self._init)

    def install(self, package: str, *args: str):
        """Builds the install/add command for a given package.

        Args:
            package (str): The package that will be installed
        """
        cmd = f"{self._install} {' '.join(args)} {package}"
        self._logger.Custom(cmd, label=self.name().upper())
        system(cmd)

    def run(self, command: str):
        """Run a command from the package.json using the notation from this package manager."""
        cmd = f"{self._run} {command}"
        self._logger.Custom(cmd, label=self.name().upper())
        system(cmd)

    def run_command(self, command: str) -> str:
        """Get the built run command for this node package manager"""
        return f"{self._run.replace(self.name(), str(which(self.name())))} {command}"


class Yarn(NPM):
    def __init__(self, logger: Log):
        super().__init__(logger=logger, init="yarn init", install="yarn add", run="yarn")


class PNPM(NPM):
    def __init__(self, logger: Log):
        super().__init__(logger=logger, init="pnpm init", install="pnpm add", run="pnpm")
