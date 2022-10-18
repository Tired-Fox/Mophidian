from __future__ import annotations


from .Base import BaseType
from .util import color, Color, Style, RESET


class Build(BaseType):
    version_format: str
    """How the generator should format the version."""
    
    default_template: str
    """The name of the default template to use for markdown files."""    
    
    def __init__(self, **kwargs) -> None:
        set_ = {'version_format': str, 'default_template': str}
        
        self.version_format = "v{}"
        self.default_template = "moph_base"
        
        self.errors = []

        for entry in kwargs:
            if entry in set_:
                if isinstance(kwargs[entry], set_[entry]):
                    setattr(self, entry, kwargs[entry])
                    del set_[entry]
                else:
                    self.errors.append(
                        color(
                            f'"',
                            color(entry, prefix=[Color.RED]),
                            '": was of type <',
                            color(type(kwargs[entry]).__name__, prefix=[Color.RED]),
                            "> but was expected to be <",
                            color(set_[entry].__name__, prefix=[Color.YELLOW]),
                            ">",
                            prefix=[Style.BOLD],
                            suffix=[RESET],
                        )
                    )
            else:
                self.errors.append(
                    color(
                        f'"',
                        color(entry, prefix=[Color.RED]),
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
