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

To prove a point, this website is built with Mophidian. So feel free to check out the [github](https://github.com/Tired-Fox/Mophidian) at any time to see examples of how to achieve different tasks.

Now lets get started.

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

## Creating a project

While the cli tool for this part is not required it makes setup go a lot faster.

To create a new project with the cli tool use the `new` command:
```bash
mophidian new
```
The tool will ask a few questions and can even help to set up integrations such as [_Sass_](https://sass-lang.com/) and [_Tailwindcss_](https://tailwindcss.com/). When finished you will have a file directory that looks similar to this.

```plaintext
project/
├ components/
├ content/
├ layouts/
├ pages/
│ └ index.html
└ static/
```

Notice the `index.html` file in the `pages/` directory. Mophidian will start you off with a sort of hello world file so you can make sure everything is working right away.

Make sure to use the `mophidian new -h` command to find out what else you can do with this command

### Initial templates

Mophidian comes with some helpful templates that are great for getting started.

You can specify a template to use with `mophidian new --template <template name>`

The includes templates include:

* `Docs` - A documentation centric template
* `Blog` - A blogging centric template
* `Blank` - The minimal default template

Don't forget to check out the website [**blog/snippets/**](/Mophidian/blog/snippets/) page to see code snippets of common things such as navigation, table of contents, styling for markdown, etc.

## Building your project

Building your project is as simple as running `mophidian build` from the root directory of all your other files. Given the user provided configurations, Mophidian will build all of the pages and static assets into the `site/` directory by default.

From here you just need to upload the contents of the `site/` directory to your preferred hosting service.