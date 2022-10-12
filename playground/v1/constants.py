code_theme = "nord"

features = {
    "highlightTags": (
f'''<!-- Highlight.js -->
<link rel="stylesheet"
href="//unpkg.com/@highlightjs/cdn-assets@11.6.0/styles/{code_theme}.min.css">
<script src="//unpkg.com/@highlightjs/cdn-assets@11.6.0/highlight.min.js"></script>'''
    ),
    
    "mathTags": (
'''<!-- Katex -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.css" integrity="sha384-IKOookmJ6jaAbJnGdgrLG5MDmzxJmjkIm6XCFqxnhzuMbfkEhGQalwVq2sYnGyZM" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.2/dist/katex.js" integrity="sha384-kSBEBJfG5+zZAKID5uvi6avDXnnOGLnbknFv6VMnVBrknlFw67TwFsY9PaD33zBI" crossorigin="anonymous"></script>'''),
    
    "onloadMath": (
        '''// Convert eq and eqn elements to formatted katex
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
}'''),
    
    "onloadHighlight": (
        '''// Highlight know languages otherwise plaintext
const toHighlight = document.querySelectorAll('code');
if (toHighlight) {
    for (const hl in toHighlight) {
        if (toHighlight[hl].className?.includes('language-')) {
            hljs.highlightElement(toHighlight[hl]);
        } else {
            toHighlight[hl].className += 'language-plaintext hljs'
        }
    }
}'''),
}