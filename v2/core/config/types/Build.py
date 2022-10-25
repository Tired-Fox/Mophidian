from __future__ import annotations


from .Base import BaseType


class Build(BaseType):
    version_format: str
    """How the generator should format the version."""

    default_template: str
    """The name of the default template to use for markdown files."""

    refresh_delay: float | int
    """The delay until the live server reloads the browser after a file change is detected."""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.version_format = "v{}"
        self.default_template = "moph_base"
        self.refresh_delay = 2.0

        self.parse_kwargs(
            cmap={
                'version_format': str,
                'default_template': str,
                "refresh_delay": [float, int],
            },
            **kwargs,
        )

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any errors. False if there are none.
        """
        return len(self.errors) > 0

    def format_errors(self) -> str:
        return '"build": {\n  ' + '\n  '.join(self.errors) + '\n}'
