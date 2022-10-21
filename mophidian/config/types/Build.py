from __future__ import annotations


from .Base import BaseType
from moph_logger import color, FColor, Style, RESET


class Build(BaseType):
    version_format: str
    """How the generator should format the version."""

    default_template: str
    """The name of the default template to use for markdown files."""

    def __init__(self, **kwargs) -> None:
        set_ = {'version_format': str, 'default_template': str, "refresh_delay": [float, int]}

        self.version_format = "v{}"
        self.default_template = "moph_base"
        self.refresh_delay = 2.0

        self.errors = []

        for entry in kwargs:
            if entry in set_:
                is_valid = True
                if isinstance(set_[entry], list):
                    if type(kwargs[entry]) not in set_[entry]:
                        is_valid = False
                else:
                    if not isinstance(kwargs[entry], set_[entry]):
                        is_valid = False

                if is_valid:
                    setattr(self, entry, kwargs[entry])
                    del set_[entry]
                else:
                    self.errors.append(
                        color(
                            f'"',
                            color(entry, prefix=[FColor.RED]),
                            '": was of type <',
                            color(type(kwargs[entry]).__name__, prefix=[FColor.RED]),
                            "> but was expected to be ",
                            ', '.join(
                                "<" + color(t.__name__, prefix=[FColor.YELLOW]) + ">"
                                for t in list(set_[entry])
                            ),
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
