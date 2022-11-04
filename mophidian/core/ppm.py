from __future__ import annotations


from os import system
from shutil import which

from moph_log import Log


def check_nodejs(logger: Log = None) -> bool:
    from shutil import which
    from subprocess import check_output

    if which("node") is not None:
        if logger is not None:
            version = check_output(['node', '--version']).decode().strip('\n').strip()
            logger.Custom(
                f"Node {version}",
                clr="magenta",
                label="Version",
            )
        return True
    else:
        if logger is not None:
            logger.Error(
                "Node.js was not found. Install it and try again or disable all integrations."
            )
        return False


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
        self, logger: Log, init: str = "init", install: str = "npm i", run: str = "npm run"
    ):
        self._init = init
        self._install = install
        self._run = run
        self._logger = logger
        self.has_node = check_nodejs(logger)

    @classmethod
    def name(cls) -> str:
        """Package manager name as lower case."""
        return cls.__name__.lower()

    @property
    def mname(self) -> str:
        """Package manager name as lower case."""
        return self.__class__.__name__.lower()

    @classmethod
    def name_title(cls) -> str:
        """Package manager name as title case."""
        name = cls.__name__.lower()
        return name[0].upper() + name[1:]

    @classmethod
    def name_upper(cls) -> str:
        """Package manager name as upper case."""
        return cls.__name__.upper()

    def __construct_parts(self, *parts) -> str:
        return " ".join([str(part) for part in parts if part not in ["", " ", None]])

    def init(self):
        """Run the init command associated with the package manager."""

        cmd = self.__construct_parts(self.name(), self._init)
        self._logger.Custom(cmd, label=self.name_title(), clr="magenta")
        system(cmd)

    def install(self, package: str, *args: str):
        """Builds the install/add command for a given package.

        Args:
            package (str): The package that will be installed
        """

        cmd = self.__construct_parts(self.name(), self._install, " ".join(args), package)
        self._logger.Custom(cmd, label=self.name_title(), clr="magenta")
        system(cmd)

    def run(self, command: str):
        """Run a command using the notation from the preferred package manager."""
        from subprocess import Popen, PIPE
        from shutil import which

        self._logger.Custom(
            self.__construct_parts(self.name(), self._run, command),
            label=self.name_title(),
            clr="magenta",
        )
        run_cmd = Popen(
            self.__construct_parts(str(which(self.name())), self._run, command),
            stdout=PIPE,
            stderr=PIPE,
        )
        run_cmd.wait()

    def run_command(self, command: str) -> str:
        """Get the built run command for this node package manager"""
        return f"{self._run.replace(self.name(), str(which(self.name())))} {command}"


class Yarn(NPM):
    def __init__(self, logger: Log):
        super().__init__(logger=logger, init="init", install="add", run="")


class PNPM(NPM):
    def __init__(self, logger: Log):
        super().__init__(logger=logger, init="init", install="add", run="")
