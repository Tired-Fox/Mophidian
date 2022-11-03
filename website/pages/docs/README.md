---
layout: docs
title: Overview
---

# Getting Started

This [SSG](./Terms/ssg.md) is not meant to replace any other SSG already out there. It is purely to
experiment with what is possible. This python package is heavily inspired by [mkDocs](https://www.mkdocs.org/), but strives to add a lot more functionality. 

This project has a few main goals:

* Be easy to use
* Implement modern web framework ideas such as:
  * components
  * layouts
  * tooling
  * integrations
  * etc...
* And most importantly, fun to use.

## Installation

There are a few dependencies for this project and they include:

* `teddecor` (Also made by me) for terminal formatting.
* `markdown` for markdown parsing
* `pymdown-extensions` for additional markdown extensions
* `python-frontmatter` to parse markdown frontmatter (metadata)
* `livereload` (TEMP) to have a hot reloading server while developing
* `watchdog` to watch files for changes and execute actions upon those changes
* `click` for CLI
* `Pygments` for code highlighting

You don't have to install these manually as these are automatically installed with the projects package.

**Install**
```bash
python3 -m pip install --upgrade mophidian
# or
pip3 install --upgrade mophidian
# or any other tool that installs pypi packages
```