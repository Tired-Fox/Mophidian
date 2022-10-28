from __future__ import annotations


from .Base import BaseType


class Integrations(BaseType):
    tailwind: bool
    """Auto use and setup tailwind css with node"""

    sass: bool
    """Auto use and setup sass with node"""

    package_manager: str
    """The users prefered package manager. Defaults to npm"""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.tailwind = False
        self.sass = False
        self.package_manager = "npm"

        self.parse_kwargs(
            cmap={
                'tailwind': bool,
                'sass': bool,
                'package_manager': str,
            },
            **kwargs,
        )

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any errors. False if there are none.
        """
        return len(self.errors) > 0
