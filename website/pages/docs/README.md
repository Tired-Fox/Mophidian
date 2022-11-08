---
layout: docs
title: Overview
---

Mophidian is a simple static site generator (SSG) that strives to be simple, easy, and powerful. Mophidian is heavily inspired by [mkDocs](https://www.mkdocs.org/), but strives to add a lot more functionality and be closer to most modern Javascript frameworks.

## Installation

There are a few dependencies for this project and they include:

**Install**
```bash
python3 -m pip install --upgrade mophidian
# or
pip3 install --upgrade mophidian
# or any other tool that installs pypi packages
```

***Note:** Here is the list of dependencies* 

* `teddecor` (Also made by me) for terminal formatting.
* `markdown` for markdown parsing
* `pymdown-extensions` for additional markdown extensions
* `python-frontmatter` to parse markdown frontmatter (metadata)
* `livereload` (TEMP) to have a hot reloading server while developing
* `watchdog` to watch files for changes and execute actions upon those changes
* `click` for CLI
* `Pygments` for code highlighting