class BaseType:
    def has_errors(self) -> bool:
        """Determines if there were errors while parsing the markdown parameters

        Returns:
            bool: True if there are any erros. False if there are none.
        """
        pass
    
    def format_errors(self) -> str:
        pass

    def key() -> str:
        return "Base"