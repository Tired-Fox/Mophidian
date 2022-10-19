class Color:
    """Ansi color codes for foreground text color.

    Options:
    - BLACK
    - RED
    - GREEN
    - YELLOW
    - BLUE
    - MAGENTA
    - CYAN
    - WHITE
    - RESET
    """

    BLACK: int = 30
    """(30) Red ansi code"""
    RED: int = 31
    """(31) Red ansi code"""
    GREEN: int = 32
    """(32) Green ansi code"""
    YELLOW: int = 33
    """(33) Yellow ansi code"""
    BLUE: int = 34
    """(34) Blue ansi code"""
    MAGENTA: int = 35
    """(35) Magenta ansi code"""
    CYAN: int = 36
    """(36) Cyan ansi code"""
    WHITE: int = 37
    """(37) White ansi code"""
    RESET: int = 39
    """(39) Reset Color ansi code"""


class Style:
    """Ansi color codes for test style.

    Options:
    - BOLD
    - NOBOLD
    - UNDERLINE
    - NOUNDERLINE
    """

    BOLD: int = 1
    """(1) Bold ansi code"""
    NOBOLD: int = 22
    """(22) No Bold ansi code"""
    UNDERLINE: int = 4
    """(4) Underline ansi code"""
    NOUNDERLINE: int = 24
    """(24) No Underline ansi code"""


RESET = 0


def color(*args, **kwargs) -> str:
    """Takes prefix and suffix ansi color codes to style the args.

        Keyword Args:
            prefix list[int]: The prefix ansi color codes
            suffix list[int]: The suffix ansi color codes
    Returns:
        str: The formatted string
    """
    prefix: str = (
        f"\x1b[{';'.join([str(s) for s in kwargs['prefix']])}m" if "prefix" in kwargs else ""
    )
    suffix: str = (
        f"\x1b[{';'.join([str(s) for s in kwargs['suffix']])}m"
        if "suffix" in kwargs
        else "\x1b[39m"
    )
    return f"{prefix}{''.join([str(arg) for arg in args])}{suffix}"
