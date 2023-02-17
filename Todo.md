# Todo

[Review](https://hynek.me/articles/testing-packaging/)
- [ ] Separate live server to it's own library/package/module
- [ ] Separate config annotation to it's own library/package/module

- [ ] General
  - [ ] Add custom errors

- [ ] Tooling
  - [ ] presets
  - [ ] integrations
    - [ ] Tailwind
    - [ ] Sass
    - [ ] Fontawesome
      - [ ] Javascript & Webfont variants
    - [ ] Math
    - [ ] read time??

## Complete

- [x] Simplify list sorting and filtering
- [x] Fix `:` not being captured in attribute value
- [x] Fix lambda's not having `built-ins` in `globals`
- [x] Fix needing to make things global to expose them to functions
- [x] Expose kwargs to python blocks as they are being processed
- [x] Global config using decorators
- [x] Tool for Pygments themes
x] global variable for creating url with website root inserted to beginning.
- [x] Automatically rip `head` element from `pages`, `layouts`, and `components` and append there children to root templates `head`
- [x] Route all files as any file name -> index.html or have special file names that stay as is in their current directory
- [x] Generate page title from file name
  - [x] `tokanize_name` from phml
  - [x] Title case the title
- [x] Get page by path
- [x] Generate site nav
  - [x] Full nav tree
  - [x] Each page's next and previous
- [x] Generate TOC from markdown file
- [x] favicon through config and head link tag
- [x] when copying elements from page head to base head, don't duplicate tags, and replace meta/title tags
- [x] Dirty/Non dirty file saving
- [x] Markdown styling
  - [x] Command for generating colored code highlights
  - [x] Add css link for code highlights
- [x] Auto add website root to href's starting with `/`. Only if they don't already start with the root.
- [x] Custom relative path plugin for markdown
- [x] Command to make new project

- [x] Any layout page change == build_hierarchy + render linked pages
- [x] New component == None
- [x] Remove Component == render all linked pages after component is removed
- [x] Update component == render all linked pages
- [x] page change == render page
- [x] static file change == re-write static file

- [ ] Live Reload Server
  - [x] All pages are referenced in dict for key(full_path) lookup
  - [x] Each file gets an epoch
    - [x] Epoch is referenced in `/livereload/{epoch}/{path}/{to}/{src}/{file}`
    - [x] src file epoch is checked with passed epoch. If a newer epoch exists, refresh the page.
  - [x] Page and Component linking on render
  - [x] Pages have all layout ancestors linked
  - [x] Update/Render individual Component/Page/Layout
    - [x] Adding and removing pages/layout from path == Full Reload
    - [x] Adding and removing component files adds to compiler but updates nothing
    - [x] Edit a page/component/layout and only have individual items that are linked Update
      - [x] layout edit means page updates
      - [x] page edit only gets page update
      - [x] component update = page update
  - [x] Trigger file updates on watchdog events
    - [x] update
    - [x] add
    - [x] remove

- [x] Sitemap
- [x] RSS

## Backlog

- [ ] Dynamic routes
  - [ ] dynamic route generation through python element
  - [ ] Generates from `content/` directory
  - [ ] `...dir` recursive catch all
  - [ ] `dir` catch all
  - [ ] `slug` file used for desired output else relevant `layout.phml` will be used.
  - [ ] `page.phml` and `layout.phml` will be given data about all the pages found for the catch all
  - [ ] Add or remove of page == full site reload
  - [ ] Edit a file
    - [ ] root page gets updated
    - [ ] updated page gets updated

Inspirational Sources:
- [mkDocs Material Theme](https://squidfunk.github.io/mkdocs-material/) ([github](https://github.com/squidfunk/mkdocs-material))
- [mkDocs](https://www.mkdocs.org/) ([github](https://github.com/mkdocs/mkdocs))
- [Algolia](https://www.algolia.com/)
- [Tailwindcss](https://tailwindcss.com/)
- [Transparent Textures](https://www.transparenttextures.com/)
- [SVG Repo](https://www.svgrepo.com/)