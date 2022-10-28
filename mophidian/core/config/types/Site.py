from __future__ import annotations

from .Base import BaseType


class Site(BaseType):
    name: str
    """The name of the site."""

    version: str
    """The version of the site EX: 0.1 or 1"""

    source: str
    """The directory to use for the source files. This equal the location of the main pages."""

    dest: str
    """The directory to put the built files into."""

    content: str
    """The directory where content files are located. These files are markdown and they are used in dynamic routes."""

    root: str
    """Root directory of the website. Used for links. Ex: https://user.github.io/project/ where project/ is the dir of the website."""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.name = "Mophidian"
        self.version = "1.0"
        self.source = "pages/"
        self.dest = "site/"
        self.content = "content/"
        self.root = ""

        self.parse_kwargs(
            cmap={
                'name': str,
                'version': str,
                'source': str,
                'dest': str,
                'content': str,
                'root': str,
            },
            **kwargs,
        )

        for value in ["source", "dest", "content"]:
            text = getattr(self, value)
            if not text.endswith("/"):
                setattr(self, value, text + "/")

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any errors. False if there are none.
        """
        return len(self.errors) > 0
