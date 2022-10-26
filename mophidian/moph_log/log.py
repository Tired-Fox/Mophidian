from __future__ import annotations
from io import TextIOWrapper
import sys

from typing import Callable, TextIO
from .encoding import encodings
from .LL import LL
from .color import color, FColor, BColor, Style, RESET


class Log:
    encoding: str
    """The encoding to output with. Default utf-8"""

    def __init__(
        self,
        output: TextIO | TextIOWrapper = sys.stdout,
        level: str = LL.ERROR,
        compare: Callable = LL.ge,
        encoding: str = "utf-8",
    ):
        self.config(output, level, compare, encoding)

    def config(
        self,
        output: TextIO | TextIOWrapper,
        level: str,
        compare: Callable,
        encoding: str = "utf-8",
    ):
        self.set_output(output)
        self.set_level(level)
        self.set_compare(compare)
        self.set_encoding(encoding)

    def set_output(self, output: TextIO | TextIOWrapper):
        """Set where logging should be printed/outputed to.

        Args:
            output (TextIO): The TextIO object to output to.

        Raises:
            TypeError: Raised when output is not a TextIO object.
        """
        if isinstance(output, TextIO) or isinstance(output, TextIOWrapper):
            self._output = output
        else:
            raise TypeError(
                f"output was {type(output)} must be of type {TextIO} or {TextIOWrapper}"
            )

    def set_level(self, level: str):
        """Set the level at which logging should occur.

        Args:
            level (str): `LL.{DEBUG,INFO,WARNING,IMPORTANT,ERROR}`

        Raises:
            TypeError: Raised when level is not a string
            TypeError: Raised when level is not an attribute in `<class 'LL'>`
        """
        if isinstance(level, str):
            if level in LL.all():
                self._level = level
            else:
                raise TypeError(
                    f"level must be an attribute in <class 'LL'>. Valid options include {', '.join(LL.all())}"
                )
        else:
            raise TypeError(f"level was {type(level)} must be of type <class 'str'>")

    def set_compare(self, compare: Callable):
        """Set the compare function for logging. Determine if logs of level that are gt, lt, eq, le, ge should be logged.

        Args:
            compare (Callable): `LL.{gt,lt,eq,ge,le}`

        Raises:
            TypeError: Raised when compare is not Callable
            TypeError: Raised when compare isn't a function from `<class 'LL'>`
        """
        if isinstance(compare, Callable):
            if compare in [LL.gt, LL.lt, LL.eq, LL.le, LL.ge] or compare.__name__ == "within":
                self._compare = compare
            else:
                raise TypeError(
                    "compare must be one of the compare functions in LL. Can be LL.gt, LL.lt, LL.eq, LL.le, LL.ge, or LL.within"
                )
        else:
            raise TypeError(f"compare was {type(compare)} must be of type Callable")

    def set_encoding(self, encoding: str):
        if isinstance(encoding, str):
            if encoding.replace("-", "_") in encodings:
                self._encoding = encoding
            else:
                raise TypeError(
                    "Invalid encoding type. Valid encoding types can be found at https://docs.python.org/3.7/library/codecs.html#standard-encodings"
                )
        else:
            raise TypeError(f"encoding was {type(encoding)} must be of type <class 'str'>")

    @classmethod
    def path(cls, *args: str, clr: str = FColor.YELLOW, spr: str = " > ") -> str:
        """Takes all the arguments, segments of path, and combines them with the given seperator and color.

        Args:
            clr (int): The color to apply to each segment of the path
            spr (str): The seperator between each segement of the path

        Returns:
            str: The formatted string
        """
        return f"{spr}".join([color(arg, prefix=[clr]) for arg in args])

    def Debug(self, *args: str):
        clr = FColor.WHITE
        if self._compare(LL.DEBUG, self._level):
            self._output.write(
                color(
                    "[",
                    color(LL.DEBUG, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()

    def Info(self, *args: str):
        clr = FColor.CYAN
        if self._compare(LL.INFO, self._level):
            self._output.write(
                color(
                    "[",
                    color(LL.INFO, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()

    def Warning(self, *args: str):
        clr = FColor.YELLOW
        if self._compare(LL.WARNING, self._level):
            self._output.write(
                color(
                    "[",
                    color(LL.WARNING, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()

    def Important(self, *args: str):
        clr = FColor.MAGENTA
        if self._compare(LL.IMPORTANT, self._level):
            self._output.write(
                color(
                    "[",
                    color(LL.IMPORTANT, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()

    def Success(self, *args: str):
        clr = FColor.GREEN
        if self._compare(LL.SUCCESS, self._level):
            self._output.write(
                color(
                    "[",
                    color(LL.SUCCESS, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()

    def Error(self, *args: str):
        clr = FColor.RED
        if self._compare(LL.ERROR, self._level):
            self._output.write(
                color(
                    "[",
                    color(LL.ERROR, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()

    def Custom(self, *args: str, clr: str = FColor.BLUE, label: str = LL.CUSTOM):
        if self._compare(LL.CUSTOM, self._level):
            self._output.write(
                color(
                    "[",
                    color(label, prefix=[clr]),
                    "] ",
                    prefix=[Style.BOLD],
                    suffix=[Style.NOBOLD],
                )
                + " ".join(args)
                + "\n"
            )
            self._output.flush()


Logger = Log(level=LL.INFO)
