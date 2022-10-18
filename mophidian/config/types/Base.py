from abc import abstractclassmethod, abstractmethod


class BaseType:
    @abstractmethod
    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any erros. False if there are none.
        """
        pass

    @abstractmethod
    def format_errors(self) -> str:
        pass

    @classmethod
    def key(cls) -> str:
        return cls.__name__.lower()
