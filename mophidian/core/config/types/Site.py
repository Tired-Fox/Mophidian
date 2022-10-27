from __future__ import annotations

from .Base import BaseType


class Site(BaseType):
    name: str
    """The name of the site."""

    version: str
    """The version of the site EX: 0.1 or 1"""

    src_dir: str
    """The directory to use for the source files. This equal the location of the main pages."""

    dest_dir: str
    """The directory to put the built files into."""

    content_dir: str
    """The directory where content files are located. These files are markdown and they are used in dynamic routes."""

    site_dir: str
    """TODO: Implement site directory and other usefull configs"""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.name = "Mophidian"
        self.version = "1.0"
        self.src_dir = "pages/"
        self.dest_dir = "site/"
        self.content_dir = "content/"
        self.site_dir = ""

        self.parse_kwargs(
            cmap={
                'name': str,
                'version': str,
                'src_dir': str,
                'dest_dir': str,
                'content_dir': str,
                'site_dir': str,
            },
            **kwargs,
        )

        for value in ["src_dir", "dest_dir", "content_dir"]:
            text = getattr(self, value)
            if not text.endswith("/"):
                setattr(self, value, text + "/")

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any errors. False if there are none.
        """
        return len(self.errors) > 0

    def format_errors(self) -> str:
        return '"site": {\n  ' + '\n  '.join(self.errors) + '\n}'

    def __str__(self) -> str:
        return f"""\
site: {{
    \"name\": {self.format(self.name)},
    \"version\": {self.format(self.version)},
    \"src_dir\": {self.format(self.src_dir)},
    \"dest_dir\": {self.format(self.dest_dir)},
    \"content_dir\": {self.format(self.content_dir)},
    \"site_dir\": {self.format(self.site_dir)},
}}\
"""
