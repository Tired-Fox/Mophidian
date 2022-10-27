from abc import abstractmethod
from distutils.log import error
from typing import MutableMapping
from moph_log import FColor, color, Style, RESET


class BaseType:
    def __init__(self):
        self.errors = []

    def format(self, value, depth: int = 0) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, dict):
            from json import dumps

            indent = ' ' * depth
            lines = dumps(value, indent=2).split("\n")

            return f"\n{indent}".join(lines)
        else:
            return str(value)

    def parse_kwargs(
        self,
        cmap: MutableMapping,
        error_formats: dict[str, str] = {"start": '"{}":', "type": "<{}>"},
        **kwargs,
    ):
        for entry in kwargs:
            if entry in cmap:
                is_valid = True
                if isinstance(cmap[entry], list):
                    if type(kwargs[entry]) not in cmap[entry]:
                        is_valid = False
                else:
                    if not isinstance(kwargs[entry], cmap[entry]):
                        is_valid = False

                if is_valid:
                    setattr(self, entry, kwargs[entry])
                    del cmap[entry]
                else:
                    self.errors.append(
                        color(
                            error_formats["start"].format(color(entry, prefix=[FColor.RED])),
                            "was of type",
                            error_formats["type"].format(
                                color(type(kwargs[entry]).__name__, prefix=[FColor.RED])
                            ),
                            "but was expected to be ",
                            ', '.join(
                                error_formats["type"].format(
                                    color(t.__name__, prefix=[FColor.YELLOW])
                                )
                                for t in list(cmap[entry])
                            ),
                            prefix=[Style.BOLD],
                            suffix=[RESET],
                        )
                    )
            else:
                self.errors.append(
                    color(
                        error_formats["start"].format(color(entry, prefix=[FColor.RED])),
                        " is not a valid option or has been found more than once.",
                        prefix=[Style.BOLD],
                        suffix=[RESET],
                    )
                )

    @classmethod
    def key(cls) -> str:
        return cls.__name__.lower()

    @abstractmethod
    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any erros. False if there are none.
        """
        pass

    @abstractmethod
    def format_errors(self) -> str:
        pass
