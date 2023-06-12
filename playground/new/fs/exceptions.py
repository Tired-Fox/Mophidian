class PathError(Exception):
    def __init__(self, message: str = "Invalid file system path") -> None:
        self.message = message
        super().__init__(self.message)
