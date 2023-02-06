from typing import Any

python_block = """\
colors = {
    'red': '#FF0000',
    'green': '#00FF00',
    'blue': '#0000FF',
    'default': '#FFFFFF'
}

def get_color(color: str) -> str:
    if color in colors:
        return colors[color]
    return colors['default']\
"""

def get_python_context(source: str) -> dict[str, Any]:
    """Get the locals built from the python source code string.
    Splits the def's and classes into their own chunks and passes in
    all other local context to allow for outer scope to be seen in inner scope.
    """

    chunks = [[]]
    lines = source.split("\n")
    i = 0

    # Split the python source code into chunks
    while i < len(lines):
        if lines[i].startswith(("def","class")):
            chunks.append([lines[i]])
            i+=1
            while i < len(lines) and lines[i].startswith((" ", "\t")):
                chunks[-1].append(lines[i])
                i+=1
            chunks.append([])
            continue

        chunks[-1].append(lines[i])
        i+=1

    chunks = ["\n".join(chunk) for chunk in chunks]
    local_env = {}

    # Process each chunk and build locals
    for chunk in chunks:
        exec(chunk, {**local_env}, local_env)

    return local_env

context = get_python_context(python_block)

input(context)
input(context["get_color"]("red"))
