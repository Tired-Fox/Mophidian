# MarkDocSSG
Use markdown to create websites

Ideas:
  - [MkDocs](https://www.mkdocs.org/getting-started/) *Python based*
  - [mynt](https://mynt.uhnomoli.com/docs/quickstart/) *Python based*
  - [Hyde](http://hyde.github.io/) base on jekyll *Python based*
  - [Cactus](https://github.com/eudicots/Cactus) used Django templating *Python based*
  - [Hugo](https://gohugo.io/)
  - [Docusarous](https://docusaurus.io/)
  - [Astro](https://astro.build/)
  - [SvelteKit](https://kit.svelte.dev/)
  - [mdBook](https://rust-lang.github.io/mdBook/) *Rust based*
 
  - [Highlight.js](https://highlightjs.org/)
  - [Markdown](https://pypi.org/project/Markdown/) [docs](https://python-markdown.github.io/reference/)
    - [Plugins](https://python-markdown.github.io/extensions/)
  
Main idea is that it mimics what major javascript frameworks are doing.
While this project strives to reach something that can create a doc's page on the level of mkdoc it also strives to be a website generator as well.

File Structure and Workflow:
    - pages
      - Can be normal html
      - Can be md files
      - Can be custom python files
        - methods return html string while classes must inherit from component class
      - Each named file gets it's own dir. index and README files stay put but override duplicates
    - components
      - Python functions and classes that returns formatted html
      - Unique importer to retrieve components and put them in templates
    - templates
      - Jinja templates
      - Custom python templating with classes and functions that convert to jinja
    - static 
      - assets that will remain untouched. files and directories are translated to the root of the server
    - config.toml or config.yml
      - Site name
      - Site navigation
      - Global variables
      - Environment variables
      - Toggle Features
      - Override styling
      - Global toggles

Guides for:
    - Jinja templating and how it can be used in this SSG
    - Markdown-it and how to add plugins for this SSG
    - Live Serve
    - Custom python templating/component system
    - Markdown flavor guide

Minimal viable product would be the ability to take markdown files and generate them to a static website with auto generated or predefined navigation.

Stretch goals include the ability to customize the css, use sass, live-server, components, custom templates, python based tailwindcss clone, searching, default component injection into markdown similar to @nuxt/content(v1 and v2), and much more.

Features:
  * site-map
  * live-server
  * components
  * templating
  * custom tailwindcss clone/bootstrap
  * searching
  * Inject custom components into markdown
  * Themes are just predefined named templates

Markdown:
    - [PyMdown](https://facelessuser.github.io/pymdown-extensions/#overview)
    - [Sup](https://github.com/jambonrose/markdown_superscript_extension)
    - [Sub](https://github.com/jambonrose/markdown_subscript_extension)
    - [Del and Ins](https://github.com/honzajavorek/markdown-del-ins)
    - [Katex math](https://gitlab.com/mbarkhau/markdown-katex)
    - **Built In** (markdown.extenxions...)
      - Extra (.extra)
        - Abbreviations (.abbr)
        - Attribute List (.attr_list)
        - Definition List (.def_list)
        - Footnotes (.footnotes)
        - Markdown in HTML (.md_in_html)
        - Tables (.tables)
      - New Line to Break (.nl2br)
      - SmartyPants (.smarty)
      - Wiki Links (.wikilinks)
    - **Custom to add copy button and filename to code blocks?**
    - Add fontawesome webfont and the icons plugin to allow users to insert fontawesome icons