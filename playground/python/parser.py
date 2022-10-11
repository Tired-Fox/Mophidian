from pprint import pprint
from markdown_it import MarkdownIt
import frontmatter

import mdit_py_plugins
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.texmath import texmath_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

# INIT Markdown_It
md = (
    MarkdownIt("gfm-like", {"typographer": True})
    .use(deflist_plugin)
    .use(footnote_plugin)
    .use(tasklists_plugin)
    .use(texmath_plugin)
    .use(anchors_plugin, permalink=True, min_level=2, max_level=4, permalinkSymbol="#")
    .enable(["replacements", "smartquotes"]))

files = ['sample', 'Todo']

for file in files:
    # Retrieve the markdown files contents
    with open(f'{file}.md', 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    # Parse the frontmatter from the content
    metadata, content = frontmatter.parse(content)

    pprint(metadata) #! DEBUG ONLY
    code_theme = "nord"
    onLoadLogic = (
 '''    window.onload = () => {
    // Highlight know languages otherwise plaintext
    const toHighlight = document.querySelectorAll('pre code');
    if (toHighlight) {
        for (const hl in toHighlight) {
            if (toHighlight[hl].className?.includes('language-')) {
                hljs.highlightElement(toHighlight[hl]);
            } else {
                toHighlight[hl].className += 'language-plaintext hljs'
            }
        }
    }

    // Convert eq and eqn elements to formatted katex
    const toConvert = document.querySelectorAll('eq, eqn');
    if (toConvert) {
        for (const math in toConvert) {
            if (toConvert[math].localName === "eqn") {
                toConvert[math].parentElement.classList.add('math-block');
            }
            if (toConvert[math].innerText) {
                let mathConverted = katex.render(toConvert[math].innerText, toConvert[math]);
            }
        }
    }
}''')

    # Render content and inject frontmatter
    with open(f'{file}.html', '+w', encoding='utf-8') as output_file:
        output_file.write(
    f'''<!doctype html>
    <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            
            <title>{metadata['title'] if 'title' in metadata else 'Document'}</title>
            
            <link rel="stylesheet" href="style.css">
            
            <!-- Highlight.js -->
            <link rel="stylesheet"
        href="//unpkg.com/@highlightjs/cdn-assets@11.6.0/styles/{code_theme}.min.css">
            <script src="//unpkg.com/@highlightjs/cdn-assets@11.6.0/highlight.min.js"></script>            
            
            <!-- Katex -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.css" integrity="sha384-IKOookmJ6jaAbJnGdgrLG5MDmzxJmjkIm6XCFqxnhzuMbfkEhGQalwVq2sYnGyZM" crossorigin="anonymous">
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.js" integrity="sha384-kSBEBJfG5+zZAKID5uvi6avDXnnOGLnbknFv6VMnVBrknlFw67TwFsY9PaD33zBI" crossorigin="anonymous"></script>
            
            <!-- Onload -->
            <script>
                {onLoadLogic}
            </script>
        </head>
        
        <body>
            <article>
                {md.render(content)}
            </article>
        </body>
    </html>''')