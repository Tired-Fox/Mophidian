from subprocess import run
from tcfg import cfg, Option, PathType
from mophidian import Plugin

class Pdoc(Plugin):
    class Config(cfg):
        format: Option["google", "markdown", "numpy", "restructuredtext"] = "google"
        """Docstring format. Options: markdown, google, numpy, restructuredtext Default `google`."""
        source: PathType
        """Source module by path."""
        out: PathType = "api/"
        """Output directory relative to website root."""
        templates: PathType
        """Directory to pdoc override templates."""
        mermaid: bool
        """Flag for rendering mermaid diagrams."""
        math: bool
        """Flag for rendering Latex math."""

    def pre(self, _):
        flags = [self.config.source, f"-d {self.config.format}"]
        if self.config.out != "":
            flags.append(f"-o {self.config.out}")
        if self.config.templates != "":
            flags.append(f"-t {self.config.templates}")
        if self.config.mermaid:
            flags.append("--mermaid")
        if self.config.math:
            flags.append("--math")
        run(f"pdoc {' '.join(flags)}")
