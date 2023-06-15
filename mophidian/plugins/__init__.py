class Plugin:
    __slots__ = ("config")
    def __init__(self, data: dict):
        if "Config" in self:
            self.config = self.__class__.Config(data)

    def __contains__(self, __key: str) -> bool:
        return hasattr(self, __key)

    # TODO: Get data to pass to file during compilation
    # def data(self, file: File, config: MophConfig):
    #     pass

    # TODO: Call to run commands in post build
    # def post(self, config: MophConfig):
    #     pass
