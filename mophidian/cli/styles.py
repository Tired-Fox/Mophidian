from pathlib import Path
from re import match
from subprocess import run
import sys

from teddecor import Logger, TED

from mophidian.config import CONFIG

pygmentize_examples =  TED.parse('*See examples of each style at \
_[@Fcyan~https://pygments.org/styles/]Pygements Website')

choose_style_prompt = TED.parse(
                    "*\\[[@Fyellow]Prompt[@F]\\] Enter a style to generate or leave blank \
to skip: "
) + "\x1b[1;31m"

class Style:
    def __init__(self, lines: list[str]) -> None:
        self.name = ""
        self.desc = ""
        self._parse_style(lines[0])
        self._parse_desc(lines[1:])

    def _parse_style(self, line: str):
        name = match(r" *\* *([a-zA-Z_\-]+) *: *", line.strip())
        if name is not None:
            self.name = name.group(1)

    def _parse_desc(self, lines: list[str]):
        lines = [line.strip() for line in lines if line.strip() != ""]
        self.desc = "".join(lines)

    def __repr__(self) -> str:
        return self.name

def list_styles() -> str:
    """List the pygmentize styles."""
    output = run('pygmentize -L style', check=True, capture_output=True).stdout
    if output is not None:
        output = output.decode('unicode_escape').replace("\r\n", "\n")
        output = output.split("\n")
        output = output[output.index('~~~~~~~')+1:]
        styles = []
        for line in output:
            if line.strip().startswith("*"):
                styles.append([line])
            else:
                styles[-1].append(line)

        styles = [Style(lines) for lines in styles]
        for _style in styles:
            print(f"{TED.parse(f'*[@Fred$]{_style.name}')}: {TED.parse(f'*[$]{_style.desc}')}")

        print("\n" + pygmentize_examples + "\n")
        try:
            style = input(choose_style_prompt)
        finally:
            sys.stdout.write("\x1b[0m")

        return style
    return ""

def _stylesheet_header(style: str, klass: str) -> str:
    return f"""\
/*! Pygmentize: https://pygments.org/ */
/*! Generated with the command `pygmentize -S {style} -f html -a .{klass}`  */
/*? {style} Style */
"""

def generate_style(style: str):
    """Generate a pygmentize CSS given a style."""

    Logger.info(f"Generating {style!r} code style").flush()
    klass = "highlight"

    if "codehilite" in CONFIG.markdown.extension_configs:
        if "css_class" in CONFIG.markdown.extension_configs["codehilite"]:
            klass = CONFIG.markdown.extension_configs["codehilite"]["css_class"]

    output = run(
        f"pygmentize -S {style} -f html -a .{klass}",
        check=True,
        capture_output=True
    ).stdout

    if output is not None:
        dest = Path(CONFIG.site.public).joinpath(CONFIG.markdown.pygmentize.path)
        output = output.decode('unicode_escape').replace("\r\n", "\n")
        output = _stylesheet_header(style, klass) + output
        with open(dest, "+w", encoding="utf-8") as highlight_file:
            highlight_file.write(output)
        Logger.info(f"Generated code style at {dest.as_posix()!r}").flush()
    else:
        Logger.error(f"Failed to generate css for style {style!r}")

def generate_highlight(style: str = "", _list: bool = False):
    """Generate the pygmentize highlight css file."""
    if _list:
        style = list_styles()

    style = style.strip()

    if style != "":
        generate_style(style)
    else:
        Logger.error("A style name must be provided").flush()