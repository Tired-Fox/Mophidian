from pathlib import Path
from re import match
from subprocess import run
import sys

from saimll import Logger, SAIML

from mophidian.config import CONFIG

pygmentize_examples = SAIML.parse(
    "*See examples of each style at \
_[@Fcyan~https://pygments.org/styles/]https://pygments.org/styles/"
)

choose_style_prompt = (
    SAIML.parse(
        "*\\[[@Fyellow]Prompt[@F]\\] Enter a style to generate or leave blank \
to skip: "
    )
    + "\x1b[1;31m"
)


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
        self.desc = "".join(lines).strip()

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        desc = ''
        if self.desc.strip() != '':
            desc = f":\n  {SAIML.parse(f'*[$]{self.desc}')}" 
        return f"{SAIML.parse(f'*[@Fred$]{self.name}')}{desc}"


def get_styles() -> list[Style]:
    output = run("pygmentize -L style", check=True, capture_output=True).stdout
    styles = []
    if output is not None:
        output = output.decode("unicode_escape").replace("\r\n", "\n")
        output = output.split("\n")
        output = output[output.index("~~~~~~~") + 1 :]
        for line in output:
            if line.strip().startswith("*"):
                styles.append([line])
            else:
                styles[-1].append(line)

        styles = [Style(lines) for lines in styles]
    styles.sort(key=lambda s: s.name)
    return styles


def print_styles():
    styles = get_styles()
    if len(styles) > 0:
        for _style in styles: 
            print(_style)
        print("\n" + pygmentize_examples + "\n")


def input_style() -> str:
    """List the pygmentize styles."""
    styles = get_styles()
    if len(styles) > 0:
        print_styles()
        try:
            style = input(choose_style_prompt)
        finally:
            sys.stdout.write("\x1b[0m")

        return style
    return ""


def _stylesheet_header(style: str, klass: str) -> str:
    return f"""\
/* Pygmentize: https://pygments.org/ */
/* Command: pygmentize -S {style} -f html -a .{klass}  */
/* Style: {style} */
"""


def generate_style(style: str):
    """Generate a pygmentize CSS given a style."""

    Logger.info(f"Generating {style!r} code style").flush()
    klass = "code-highlight"

    if "codehilite" in CONFIG.markdown.configs:
        if "css_class" in CONFIG.markdown.configs["codehilite"]:
            klass = CONFIG.markdown.configs["codehilite"]["css_class"]

    output = run(
        f"pygmentize -S {style} -f html -a .{klass}", check=True, capture_output=True
    ).stdout

    if output is not None:
        dest = Path(CONFIG.paths.public).joinpath(CONFIG.markdown.pygmentize.path)
        output = output.decode("unicode_escape").replace("\r\n", "\n")
        output = _stylesheet_header(style, klass) + output
        with open(dest, "+w", encoding="utf-8") as highlight_file:
            highlight_file.write(output)
        Logger.info(f"Generated code style at {dest.as_posix()!r}").flush()
    else:
        Logger.error(f"Failed to generate css for style {style!r}")


def generate_highlight(style: str = ""):
    """Generate the pygmentize highlight css file."""

    style = style.strip()

    if style == "":
        style = input_style()

    if style == "":
        Logger.Error("A style name must be provided")
    else:
        generate_style(style)
