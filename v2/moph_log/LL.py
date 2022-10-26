from typing import Callable


class LL:
    """The log level

    - DEBUG     : Contains information relavant to development
    - INFO      : Contains information that can be ignored if needed
    - WARNING   : Something that should be read but doesn't need action
    - IMPORTANT : Something that needs to be read
    - SUCCESS   : Something that needs to be read
    - ERROR     : Something that needs action or is critical to a process
    """

    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARNING: str = "WARNING"
    IMPORTANT: str = "IMPORTANT"
    ERROR: str = "ERROR"
    SUCCESS: str = "SUCCESS"
    CUSTOM: str = "CUSTOM"
    _order = [DEBUG, INFO, WARNING, IMPORTANT, SUCCESS, ERROR, CUSTOM]

    @classmethod
    def all(cls) -> list[str]:
        """Get all of the levels in the correct priority order.

        - DEBUG
        - INFO
        - WARNING
        - IMPORTANT
        - SUCCESS
        - ERROR
        - CUSTOM

        Returns:
            list[str]: List of all log levels.
        """
        return cls._order

    @classmethod
    def base(cls, *args: str) -> list[str]:
        """Get base list of levels.

        - INFO
        - WARNING
        - ERROR

        Arguments:
            *args (str): Additional levels to add

        Returns:
            list[str]: List of the base levels.
        """
        levels: list[str] = cls._order[1:4]
        levels.extend(args)
        return levels

    @classmethod
    def extended(cls, *args: str) -> list[str]:
        """Get extended list of levels. Excludes DEBUG

        - INFO
        - WARNING
        - IMPORTANT
        - SUCCESS
        - ERROR

        Arguments:
            *args (str): Additional levels to add

        Returns:
            list[str]: List of the base levels.
        """
        levels: list[str] = cls._order[1:]
        levels.extend(args)
        return levels

    @classmethod
    def gt(cls, level1: str, level2: str) -> bool:
        """Returns if the first level is greater than the second.

        Args:
            level1 (str): The first level to compare
            level2 (str): The second level to compare

        Returns:
            bool: True if level1 is greater than level2
        """
        return cls._order.index(level1) > cls._order.index(level2)

    @classmethod
    def lt(cls, level1: str, level2: str) -> bool:
        """Returns if the first level is less than the second.

        Args:
            level1 (str): The first level to compare
            level2 (str): The second level to compare

        Returns:
            bool: True if level1 is less than level2
        """
        return cls._order.index(level1) < cls._order.index(level2)

    @classmethod
    def eq(cls, level1: str, level2: str) -> bool:
        """Returns if the first level is equal to the second.

        Args:
            level1 (str): The first level to compare
            level2 (str): The second level to compare

        Returns:
            bool: True if level1 is equal to level2
        """
        return cls._order.index(level1) == cls._order.index(level2)

    @classmethod
    def le(cls, level1: str, level2: str) -> bool:
        """Returns if the first level is less than or equal to the second.

        Args:
            level1 (str): The first level to compare
            level2 (str): The second level to compare

        Returns:
            bool: True if level1 is less than or equal to level2
        """
        return cls._order.index(level1) <= cls._order.index(level2)

    @classmethod
    def ge(cls, level1: str, level2: str) -> bool:
        """Returns if the first level is greater than or equal to the second.

        Args:
            level1 (str): The first level to compare
            level2 (str): The second level to compare

        Returns:
            bool: True if level1 is greater than or equal to level2
        """
        return cls._order.index(level1) >= cls._order.index(level2)

    @classmethod
    def within(cls, *args: list[str] | str) -> Callable:
        """Take a list of levels and checks if the logged level is in that list.

        Args:
            *args (list[str] | str): List of levels to use for comparing.

        Returns:
            Callable: Lambda function that takes the currently logged level and compares it against the valid list.
        """
        levels = []
        for arg in args:
            if isinstance(arg, list):
                levels.extend(arg)
            elif isinstance(arg, str):
                levels.append(arg)

        def within(level, _):
            return level in levels

        return within
