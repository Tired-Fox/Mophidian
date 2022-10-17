# MarkDocSSG
Use markdown to create websites

## Ideas:
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

___

## Rules and how things work

___

### Page generation and configuration

Important file structure:
- ***Directories***
  - **components**
  - **pages**
  - **content**
  - **static**
  - **templates**

- ***Files***
  - Content is written in `.md` (markdown)
  - Templates and components are written html files. They use the [Jinja2](https://palletsprojects.com/p/jinja/) templating language to inject data.
  - Non-compiled assets, assets that won't be transformed, should go into the static folder. This is a 1-1 translation to the final file structure. Nothing is changed just copied over.
  - The pages are written in html(jinja2) or markdown.

Files in pages get their own directory where possible. This is more to follow file based routing and how most hosting services automatically load the index.html file when given a directory. So `pages/about/me.md` == `pages/about/me/index.html` when compiled. `index.md`, `readme.md`, `README.md`, and `index.html` all compile to a index.html file. A `index.html` file would take priority and all other files would be ignored. You can also specify the index.html file outside of the directory and have it compile into that directory. It is easier to show so here are the before and after:
    
**Before compiling:**
```plaintext
pages
    - about.md
    - about/
      - me.md
    - index.html
```

**After compiling:**
```plaintext
pages
    - about/
      - index.html
      - me/
        - index.html
    - index.html
```

**Url's**
```plaintext
website/
website/about/
website/about/me/
```

Since the compiler is already filtering, transforming, and working it's magic, it will also automatically generate a sitemap.xml, sitemap.xml.gz, and rss.xml along with providing the url's as data to each template.

**GOAL: All data relavent from website generation and user specification is provided to each template.**

Framework provided information:
- ***Pre rendered / Computed*** *(Nested information accessed with `{{ <variable>. }}`)*
  - **site**: This is the site information like name, url, uri, description, etc. (`{{ site.name }}`)
  - **env** : This is the global variables the user wants to make available to every templates. (`{{ env.socials.github }}`)
  - **meta**: The meta data that is retrieved from frontmatter in a markdown file. (`{{ meta.tags }}`)
  - **content**: Gives access to the information for each page defined in `content/` directory. (`{{ content['file_name without extension'].description }}`)

- ***Computed during site generation***
  - **hooks**: *(Maybe not possible with jinja2)* Idea is a work in progress. Some sort of way of including methods or functions then allowing the user to specify that they want to retrieve that data. (`{{ hook.get_weather() }}`)
  - **components**: This is the list of all components specified in the components folder. (`{% include components.dropdown %}`)
  - **templates**: Gives access to all user and internally defined templates. (`{% include templates.nav %}`) or (`{% extend templates.base_template %}`)
  

- Users may also include other templates as needed using a string ex. `{% include "../path/some_template" %}`.

When using markdown files in the pages directory a user must specify a template in the frontmatter or a default template in the config.

HTML files in the pages directory are automatically processed as a full page template. As in somewhere it must include the html elements `<!DOCTYPE html>`, `<html></html>`, and `<body></body>`. The framework will provide the same information as mentioned above.

Framework provides built in `[slug]` and `[...slug]` features which are "catch all" files. `[slug]` is a catch all for files in a directory while `[...slug]` is a catch all for recursive directories.

- `pages/articles/[slug].html` would map to any file in the `content/articles/` directory (`content/articles/*.md`)
- `pages/articles/[...slug].html` would map to any file and directory of `content/articles` (`content/articles/**/*.md`)
___
