# Todo

- [x] Global config using decorators
- [ ] Global reference to pages, components, and layouts

```
components:
  - **/*.phml 
pages:
  - **/*:
    - *.phml
    - +layout.phml
```

* `+layout.phml` files have a `<slot />` tag that is placeholder for markdown and html files
  * Must be a full html file
  * html/phml files in same directory can be partials
* When layouts and pages are parsed they are checked for components and a double link is created between page and component.
  * When a component is updated all linked pages are updated
  * When a layout is updated all pages are updated
* Flask is utilized while developing and debugging the website for live updates and debugging component injection
* When the site is compiled for deployment it is static and dynamic routes are compiled to static files

## Backlog

- [ ] Fontawesome integration
  - [ ] Javascript & Webfont variants
- [ ] Math plugin/Integration
- [ ] Add custom errors
- [ ] Tool for Pygments themes
- [ ] Tool for selecting presets
- [ ] Tool for adding/removing integrations
- [ ] Support for bootstrap??
- [ ] Support for read time??
- [ ] Custom wsgi_app server with live reloading including watchdog


Inspirational Sources:
- [mkDocs Material Theme](https://squidfunk.github.io/mkdocs-material/) ([github](https://github.com/squidfunk/mkdocs-material))
- [mkDocs](https://www.mkdocs.org/) ([github](https://github.com/mkdocs/mkdocs))
- [Algolia](https://www.algolia.com/)
- [Tailwindcss](https://tailwindcss.com/)
- [Transparent Textures](https://www.transparenttextures.com/)