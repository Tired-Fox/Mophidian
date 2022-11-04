---
title: 'M-Ophidian'
description: 'A python based static site generator (SSG). Inspired from mkDocs, next.js, vue.js, nuxt.js, mynt, astro, and just about every other SSG.'
img: 'https://wallpaperaccess.com/full/344618.jpg'
tags: [Python, SSG, Jinja2, Live-Server, Website, M-Ophidian]
---

# Mophidian - A python based SSG
Use markdown to create websites

## Ideas:

**Inspiration**
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
  
Code highlight done with CodeHilite plugin with `pygmentize -S <theme> -f html -a .codehilite > styles/highlight.css` setting the theme. `pygmentize -L style` for list of themes.

Add font awesome support by downloading the webfonts and adding css files. https://fontawesome.com/docs/web/setup/host-yourself/webfonts. Add an integration for this.

The core ideas behind this SSG/framework is the same as all the large Javascript frameworks. So in a way, if you used any type of Javascript framework, then this project should be fairly easy to use.

While this project strives to reach something that can create a doc's page on the level of mkDocs it also strives to be a generic website generator as well.

File Structure and Workflow:
- pages
  - Can be normal html
  - Can be md files
  - Each named file gets it's own dir. index and README files stay put but override duplicates
- components
  - Each one a Jinja2 snippet
  - Unique importer to retrieve components and put them in templates
- layouts
  - Jinja2 templates, meant to be a layout for the page.
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

There will be guides for:
- Jinja templating and how it can be used in this SSG
- Markdown-it and how to add plugins for this SSG
- Live Server
- Markdown flavor guide (Specific to the default markdown plugins in this SSG)

Minimal viable product would be the ability to take markdown files and generate them to a static website with auto generated or predefined navigation.

Stretch goals include the ability to customize the css, use sass, live-server, components, custom templates, python based tailwindcss clone, searching, default component injection into markdown similar to @nuxt/content(v1 and v2), and much more.

Features:
  * site-map
  * live-server
  * components
  * templating
  * custom tailwindcss clone/bootstrap??
  * searching
  * Inject custom components into markdown. Requires custom python-markdown plugins/manipulation
  * Themes are just predefined named templates/layouts

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
  - **layouts**

- ***Files***
  - Content is written in `.md` (markdown)
  - Layouts and components are written html files. They use the [Jinja2](https://palletsprojects.com/p/jinja/) templating language to inject data.
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

**GOAL: All data relevant from website generation and user specification is provided to each template.**

Framework provided information:
- ***Pre rendered / Computed*** *(Nested information accessed with `{{ <variable>. }}`)*
  - **site**: This is the site information like name, url, uri, description, etc. (`{{ site.name }}`)
  - **env** : This is the global variables the user wants to make available to every templates. (`{{ env.socials.github }}`)
  - **meta**: The meta data that is retrieved from frontmatter in a markdown file. (`{{ meta.tags }}`)
  - **pages**: Gives access to the information for each page defined in the `content/` and `pages/` directories. (`{{ pages['recipes/chocolage_cake'].description }}`)
  - **content**: The rendered html from a markdown file

- ***Computed during site generation***
  - **hooks**: *(Maybe not possible with jinja2)* Idea is a work in progress. Some sort of way of including methods or functions then allowing the user to specify that they want to retrieve that data. (`{{ hook.get_weather() }}`)
  - **components**: This is the list of all components specified in the components folder. (`{% include components.dropdown %}`)
  - **layouts**: Gives access to all user, and internally defined layouts. (`{% include layouts.nav %}`) or (`{% extend layouts.base_template %}`)
  

- Users may also include other templates as needed using a string. Ex. `{% include "../path/some_template" %}`.

When using markdown files in the pages directory a user must specify a layout in the frontmatter or a default layout in the config. If neither is chosen a basic built-in layout will be used.

HTML files in the pages directory are automatically processed as full page layouts. As in, somewhere in the file, it must include the html tags/elements; `<!DOCTYPE html>`, `<html></html>`, and `<body></body>`. The framework will provide the same information as mentioned above.

Framework provides built in `[slug]` and `[...slug]` features which are "catch all" files. `[slug]` is a catch all for files in a directory while `[...slug]` is a catch all for recursive directories.

- `pages/articles/[slug].html` would map to any file in the `content/articles/` directory (`content/articles/*.md`)
- `pages/articles/[...slug].html` would map to any file and directory of `content/articles` (`content/articles/**/*.md`)
- 
---

### Workflow

Begin by creating a new project. Right now you need to manually create all the files.
A valid file structure will look like the text below. You can add any other folders and files outside of this structure; they will most likely be ignored.

```plaintext
project
├ components/
│ └ */**/.html
├ content/
│ └ */**/*.html
├ layouts/
│ └ */**/*.html
├ pages/
│ ├ */**/*.md
│ └ */**/*.html
└ static/
  └ */**/*.*
```

When you build or serve the project you will get a `site/` folder added. This is all the files compiled together. These are also the files you can host on a server.

Eventually, when there is an automated way of creating a new project, you will also get example files in the main folders. There will be example layouts, components, content, dynamic routes, pages, and static assets.

Enjoy the use of a live reloading server that incrementally builds your changes that can be seen immediately. 

**File Layout**

Here I will attempt to describe what can be in each file and what a good format may be.

* Lets start with components.
 
Components are html files. I chose this format because most text editors have great language support and highlighting for html. Components are meant to be small reusable snippets that you want in your website. The components filename is converted to the name of the component so that is what you use to access it in your layouts and templates.

Because of the nature of HTML and CSS you can include specific styling in a `<style>` tag at the root level of the component. this means you could make a component that looks like this.

```html
<div id="header">
    <a href="/">Home</a>
    <div id="nav">
        <a href="/blog">blog</a>
        <a href="/news">news</a>
    <div>
</div>
<style>
    * {
        box-sizing: border-box;
    }

    #header {
        display: flex;
        width: 100%;
        justify-content: space-between;

        padding-block: 1rem;
        padding-inline: 5rem;
    }

    #header a{
        color: black;
        text-decoration: none;
    }

    #header a:hover {
        text-decoration: underline;
    }
</style>
```

After this component is created in the `components/` directory, you can use it in any html template file with `{% include cmpt.header %}`.

**Other html template files**

I recommend reading the [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/) from Jinja2 as that is the full power of what you can do. You follow the same rules and logic, with added ease of use with mophidian giving access to your components and layouts without having to type in the path. However that is an option too, even though it is not recommended.

Say that you created a template/layout named base.html in the `layouts/` directory. You can do the following to extend a template/layout:

```html[some_layout.html]
{% extend lyt.base %}
<head>
    {%- block header}
    {{ super() }}
    <link rel="stylesheet" href="/css/header.css">
    {%- endblock %}
</head>
{%- block content %}
    {{ content }}
{%- endblock %}
```

Or if you implemented the `base.html` file somewhere else you can do something like this.

```html[some_layout.html]
{% extend "path/to/layout/base.html" %}
<!-- ... Override blocks here ... -->
```

**Markdown files**

Markdown files are the easiest. If you want data variables from the file you can use frontmatter. 

It will look a little like this:

```yaml
---
title: Some Title Goes Here
readTime: 3 min
.
.
.
---
```

This framework then opens these variables up to you with a variable called `meta`. You can call it directly for a layout page that is for a markdown file. Otherwise, if you decide to access the meta file form one of the pages/contents variables you can do `pgs[idx].meta` or `cnt[idx].meta`.