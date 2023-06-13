from phml import HypertextManager

print("NAME", __name__)
from ..fs import FileSystem, FileType
from ..config import Config

class Compiler:
    __slots__ = ("phml", "config", "file_system", "public", "components", "scripts")

    def __init__(self):
        self.phml: HypertextManager = HypertextManager()
        self.config: Config = Config()

        self.file_system: FileSystem = FileSystem(self.config.paths.files).glob("**/*")
        self.public: FileSystem = FileSystem(self.config.paths.public).glob("**/*")
        self.components: FileSystem = FileSystem(self.config.paths.components).glob("**/*.phml")
        self.scripts: FileSystem = FileSystem(self.config.paths.scripts).glob("**/*.py")

        for component in self.components.walk(FileType.File):
            self.phml.add(component.path, ignore=component.ignore)

        for script in self.scripts.iter(FileType.File):
            self.phml.add_module(script.path, base="moph", ignore=self.scripts.root.ignore)
