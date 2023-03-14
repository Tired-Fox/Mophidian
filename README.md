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
  
Code highlight done with CodeHilite plugin with `pygmentize -S <theme> -f html -a .highlight > styles/highlight.css` setting the theme. `pygmentize -L style` for list of themes.

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

### File Structure

Mophidian uses a custom language called [`phml`](https://github.com/Tired-Fox/phml). This language was inspired by javascript frameworks similar to Vue.js. The language support python blocks inside `<python>` tags and inline python for conditions and in replacements. With this phml also has a built in component system. This works how you think it would in other javascript languages. You just need to load the component into the compiler then you can use the component anywhere in your phml code.

A simple phml page may look something like this.

```html
<!-- index.phml -->
<!DOCTYPE html>
<html>
  <head>
    <title>Example</title>
  </head>

  <body>
    <h1>Hello World</h1>
  </body>
</html
```

Which ends up looking exactly the same when it is compiled to html. Phml allows users to pass in extra variables into the compiler which will be exposed to the phml file as it is being compiled/rendered. You can compare this to something similar to [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) and how it handles data.

Here is an example of how Jinja2 handles variables and how it uses them. 

```python
from jinja2 import Environment
env = Environment()
template = env.get_template("sample.html")
template.render(variables="go", here=True, errors=["er1", "er2"])
```

```html
<!-- sample.html -->
<!DOCTYPE html>
<html>
  <head>
    <title>{{ variables }}</title>
  </head>
  <body>
    {% if here %}
      <p>Right here</p>
    {% else %}
      <p>Not Here</p>
    {% endif %}
    <ul>
      {% for error in errors %}
      <li>{{ error }}</li>  
      {% endfor %}
    </ul>
  </body>
</html>
```

Phml is similar in some way. Below is how the same example is written in phml.

```python
from phml import PHML

phml = PHML()

phml.load("sample.phml")
phml.render(variables="go", here=True, errors=["er1", "er2"])

# or with shorthand
phml.load("sample.phml").render(variables="go", here=True, errors=["er1", "er2"])
```

```html
<!-- sample.phml -->
<!DOCTYPE html>
<html>
  <head>
    <title>{{ variables }}</title>
  </head>
  <body>
    <p @if="here">Right here</p>
    <p @else>Not Here</p>
    <ul>
      <For :each="error in errors">
        <li>{{ error }}</li>  
      </For>
    </ul>
  </body>
</html>
```

As seen above both are very similar while phml is simplier to write. Phml also has the benifit of using python itself instead of a python like syntax. Also loops retain context so any nested loop using a value from the outer scope won't break.

If you want to know more about phml check out it's [documentation](https://tired-fox.github.io/phml/phml.html)

Mophidian also has built in markdown support. Markdown plugins can be added and modified through Mophidian's configuration file. On top of the plugins Mophidian allows for use of phml components and the use of frontmatter.

Frontmatter is yaml at the start of the file. The parsed values are passed to the markdown pages layout and can be used in rendering a page.

```markdown
---
title: Sample Markdown Page
tags: ['markdown', 'example']
---

# Example Markdown

hello world
```

This above example will use title for the page title. If it isn't present then it will parse the h1 element, `# Example Markdown`, and finally if that is also missing, the markdown file name is used.

You may have noticed that it was mentioned that markdown files use layout pages. These are pages named `layout.phml`. These layouts are expected to be structured like a phml component and it must contain a `<Slot />` component. Any file that uses this layout will have it's context placed in place of the `<Slot />` component.

```html
<!-- layout.phml -->
<>
  <h1>{{ title }}</h1>
  <Slot />
</>
```

Pages inside of mophidian are similar to layouts where they are phml components. This allows for pages to be placed inside of layouts and layout can be placed inside of other layouts. All pages have the name of `page.phml` with an optional layout name seen as `page@{layout}.phml`. See the [File System](#file_system) section to see how this works.

```html
<!-- page.phml -->
<python>
  # Any python code goes here. Indentation is based on the first line with text
  message = "Hello World"
</python>

<!-- The wrapping component can be an empty tag or any 
other element but there must be only one content element -->
<>
  <p>Hello World</p>
  <a href="/">Home</>
</>

<script>
// Any script logic here
</script>

<style>
  /* Any css styles here */
</style>
```

At the root of rendering a page in Mophidian there is a base layout which fills in the structure of an html page. ```html
<!-- base.phml -->
<!DOCTYPE html>
<html>
  <head>
    <!-- default meta tags see docs for more info -->
    <title>{{ title or '' }}</title>
  </head>
  <body>
    <Slot />
  </body>
</html>
```

All nested layouts and the page are put into their appropriate slot and then eventually placed in the `<Slot />` element in the base layout. To add any other element to the `<head />` tag just use the head tag again in a layout or page. Mophidian will take all elements from these duplicate head tags and put them in the base tag. All duplicate tags are ignored. Special tags like title are replace when they are duplicated.

```html
<!-- page.phml -->
<>
  <head>
    <title>Example</title>
  </head>
  <p>This is a sample page</p>
</>
```

### File System

The file system is structured based on javascript libraries like [Astro.js](https://astro.build/). It looks something like this.

```
project
├ moph.yml 
├ public/
│ └ */**/*.*
└ src/
  ├ components/
  │ └ */**/.phml
  └ pages/
    ├ */**/*.md
    ├ */**/page.phml
    └ */**/layout.phml
```

As you can see above there are three primary objects in the root project directory. `moph.yml` is used for the Mophidian configuration. `public/` is where static assets are placed. All files and directories are one-to-one to the root of the server. `src/` is where all pages, components, layouts, and additional static files are placed.

Components are placed into their own subdirectory, `src/components/` and each file is a phml component. All components file names are used for the component name. For example, if you have a file named `Callout.phml` the component can be used with `<Callout />`. Components in subdirectories have their parent directories appended to the name recursively with each name being seperated with a dot. This can look something like this, `header/Nav.phml`, which will expose a component to use that looks like this, `<Header.Nav />`.

Page, layout, and markdown files are placed into the `src/pages` directory. There can only be one `layout.phml` and `page.phml` per directory. There can be any number of markdown files per directory, with `README.md` being equivelant to a `page.phml` page. Any layout in the same directory as a `page.phml` or markdown file with be used for that file. If there is a layout missing from the current directory, then the next parent directories layout is used. This is recursive up until the base layout. 

Mophidian supports groups. These are directories with the syntax of `(group name)`. This is a psuedo directory and is used to name a layout that is in that directory. The layout inside the root of a group inherits it's name. All other files and directories are treated as if they are located in the next parent directory. With the layout inheriting the groups name, all `page.phml` and markdown files can skip it's default assigned layout and use a specific layout. For example if you have the following file structure.

```
...
└ src/
  └ pages/
    ├ (blog)
    │ ├ layout.phml
    │ └ page.phml
    └ about/ 
      └ page@blog.phml
```

The `page.phml` file inside the `about/` directory with use the layout from the `(blog)` group. The file structure is treated like it looks like this.
```
...
└ src/
  └ pages/
    ├ layout.phml < has a layout name of blog
    ├ page.phml
    └ about/ 
      └ page@blog.phml
```

This file system logic is heavily inspired by [Svelte Kit](https://kit.svelte.dev/docs/advanced-routing#advanced-layouts-group). More about how this all works is in the Mophidian documentation.

### Features

Mophidian comes with many quality of life features with more on the way. Some of notable features include: helper methods, value shorthands, live reloading, and a CLI tool.

#### Helper Methods
- `blank(value)`: Checks if the value is `None`, `False`, or empty. Currently support lists, sets, tuples, and dicts for checking if empty
- `classnames`: Works the same as Vue.js built in [classlist attribute](https://vuejs.org/guide/essentials/class-and-style.html#binding-html-classes). It allows for conditional classes, and listing classes. Example `classnames('red', {'bold': is_bold}, ['underline', {'left-0': lalign}])`
- `filter_sort(collection, filter, key)`: Both filters and sorts a list without calling multiple methods. Uses pythons built in `filter` and `sorted` methods. First it will filter by the passed filter argument, then it will sort the collection by the passed key argument.

#### Value Shorthands
- `@` at the start of `src` and `href` html attributes. The `@` is replaced with the servers root so you don't have to type it out every time.

#### Live Reloading
Mophidian uses a custom library call `watchserver` which is built to automatically handle live reloading pages. It works by determining if it is serving an html page. If it is then it inserts a script that polls the server on a specific endpoint and checks if the current page should be refreshed. The endpoint either response with a truthy response or a falsy one. The server determines if a page should be reloaded based on if it's path fits a file pattern created by a file watch event. I recommend looking at the [watchserver documentation](https://github.com/Tired-Fox/watchserver) for more information on how this works. 

#### CLI Tool

Mophidian comes with a cli tool called `moph`. This tool comes with the ability to: create a new project, build a project, build and serve a project, build and preview a project, and generate pygmentize css.


For more information about Mophidian, check out the [documentation](https://tired-fox.github.io/Mophidian/)
