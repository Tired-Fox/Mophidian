---
header_nav: [["Sample", "/playground/web/sample.html"], ["Todo", "/playground/web/Todo.html"]]
include_highlight: True
---

## Created in Python
1. Uses Highlight.js for code block highlighting
   - [HighlightJS Styles](https://unpkg.com/browse/@highlightjs/cdn-assets@11.6.0/styles/)
2. Uses markdown-it-py to convert markdown to html
   - [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/using.html)
   - [plugins](https://github.com/executablebooks/mdit-py-plugins/tree/master/mdit_py_plugins)
   - `pip install markdown-it-py[linkify,plugins]`
3. Uses python-frontmatter to parse markdown frontmatter
   - [python-frontmatter](https://pypi.org/project/python-frontmatter/)
4. Uses toml to support python prior to 3.11
   - [toml](https://pypi.org/project/toml/)
5. Uses Jinja2 for templating the html pages
   - [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/#base-template)

