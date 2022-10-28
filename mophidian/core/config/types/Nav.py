from __future__ import annotations


from .Base import BaseType


class Nav(BaseType):
    directory_url: bool
    """Whether to use directory urls. If true then files like `foo.md` will translate to `foo/index.html`."""

    def __init__(self, **kwargs) -> None:
        super().__init__()

        self.directory_url = True

        self.parse_kwargs(
            cmap={
                'directory_url': bool,
            },
            **kwargs,
        )

    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any errors. False if there are none.
        """
        return len(self.errors) > 0
