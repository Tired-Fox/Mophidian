from __future__ import annotations


from .Base import BaseType
from util import color, FColor, Style, RESET


class Integration(BaseType):
    tailwind: bool
    """Auto use and setup tailwind css with node"""

    sass: bool
    """Auto use and setup sass with node"""

    package_manager: str
    """The users prefered package manager. Defaults to npm"""

    def __init__(self, **kwargs) -> None:
        set_ = {'tailwind': bool, 'sass': bool, 'package_manager': str}

        self.tailwind = False
        self.sass = False
        self.package_manager = "npm"

        self.errors = []

        for entry in kwargs:
            if entry in set_:
                if isinstance(kwargs[entry], set_[entry]):
                    del set_[entry]
                    setattr(self, entry, kwargs[entry])
                else:
                    self.errors.append(
                        color(
                            f'"',
                            color(entry, prefix=[FColor.RED]),
                            '": was of type <',
                            color(type(kwargs[entry]).__name__, prefix=[FColor.RED]),
                            "> but was expected to be <",
                            color(set_[entry].__name__, prefix=[FColor.YELLOW]),
                            ">",
                            prefix=[Style.BOLD],
                            suffix=[RESET],
                        )
                    )
            else:
                self.errors.append(
                    color(
                        f'"',
                        color(entry, prefix=[FColor.RED]),
                        '": ' "not a valid option or has been found more than once.",
                        prefix=[Style.BOLD],
                        suffix=[RESET],
                    )
                )

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any errors. False if there are none.
        """
        return len(self.errors) > 0

    def format_errors(self) -> str:
        return '"build": {\n  ' + '\n  '.join(self.errors) + '\n}'
