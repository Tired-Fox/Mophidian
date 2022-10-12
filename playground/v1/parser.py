
from pprint import pprint
from markdown_it import MarkdownIt
import frontmatter
import lxml.html
from os import mkdir, path

from jinja2 import Environment, FileSystemLoader

import mdit_py_plugins
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.texmath import texmath_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from components.SVG import flask
from constants import features

def san(text: str, tabs: int = 0) -> str:
    lines = text.strip().replace('\t', '    ').split('\n')
    
    def get_leading(text: str) -> int:
        return len(text) - len(text.lstrip())
    
    leading = get_leading(lines[0])
    
    def format_lines(flines: list[str]) -> list[str]:
        for i, line in enumerate(flines):
            nl = get_leading(line)
            print(nl, leading, len(tabs*'>'), len((nl - leading) * '-'))
            
            flines[i] = (tabs*'    ') + ((nl - leading) * ' ') + line.lstrip()
            
        return flines
    
    return f"\n".join(format_lines(lines))

try:
    import tomllib
except ImportError:
    import toml
    tomllib = toml
    
with open('pymarkssg.toml', 'r') as config:
    config = tomllib.load(config)

# INIT Markdown_It
md = (
    MarkdownIt("gfm-like", {"typographer": True})
    .use(deflist_plugin)
    .use(footnote_plugin)
    .use(tasklists_plugin)
    .use(texmath_plugin)
    .use(anchors_plugin, permalink=True, min_level=2, max_level=4, permalinkSymbol="#")
    .enable(["replacements", "smartquotes"]))

files = ['sample', 'Todo', 'parser']

for file in files:
    # Retrieve the markdown files contents
    with open(f'pages/{file}.md', 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    # Parse the frontmatter from the content
    metadata, content = frontmatter.parse(content)
    
    copyrightYear = '2022'

    if not path.exists('../web'):
        mkdir('../web')
    
    environment = Environment(loader=FileSystemLoader("templates/"))
    try:
        template = environment.get_template(metadata['template'] if 'template' in metadata else "base/markup.jinja")
    except:
        template = environment.get_template("base/markup.jinja")
    
    # print(metadata)
    
    footnote_anchor = '''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="1rem" height="1rem">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 15L3 9m0 0l6-6M3 9h12a6 6 0 010 12h-3" />
    </svg>'''
    
    sub = "↩︎"

    # Render content and inject frontmatter
    with open(f'site/{file}.html', '+w', encoding='utf-8') as output_file:
        options = {
            "content": md.render(content),
            "copyrightYear": copyrightYear,
            "copyrightOwner": "Zachary Boehm",
            "header_logo": "<h5>Zachary Boehm</h5>",
        }
        options.update(metadata)
        options.update(features)
        if 'global' in config and 'variables' in config['global']:
            options.update({"global": config['global']['variables']})
        
        raw = template.render(options)
        # raw = raw.replace(sub, footnote_anchor)
        output_file.write(raw)
    
