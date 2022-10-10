from cgitb import text
from pprint import pprint
from markdown_it import MarkdownIt
import frontmatter

import mdit_py_plugins
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.texmath import texmath_plugin

# INIT Markdown_It
md = (
    MarkdownIt("gfm-like", {"typographer": True})
    .use(attrs_plugin)
    .use(footnote_plugin)
    .use(texmath_plugin)
    .use(anchors_plugin, permalink=True, min_level=2, max_level=3)
    .enable(["replacements", "smartquotes"]))

# Retrieve the markdown files contents
with open('sample.md', 'r', encoding='utf-8') as md_file:
    content = md_file.read()

# Parse the frontmatter from the content
metadata, content = frontmatter.parse(content)

pprint(metadata) #! DEBUG ONLY

# Render content and inject frontmatter
with open('text.html', '+w', encoding='utf-8') as output_file:
    output_file.write(
f'''<!doctype html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <title>{metadata['title'] if 'title' in metadata else 'Document'}</title>
        
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.min.css" integrity="sha384-bYdxxUwYipFNohQlHt0bjN/LCpueqWz13HufFEV1SUatKs1cm4L6fFgCi1jT643X" crossorigin="anonymous">
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.min.js" integrity="sha384-Qsn9KnoKISj6dI8g7p1HBlNpVx0I8p1SvlwOldgi3IorMle61nQy4zEahWYtljaz" crossorigin="anonymous"></script>
    </head>
    
    <body>
        {md.render(content)}
    </body>
</html>''')