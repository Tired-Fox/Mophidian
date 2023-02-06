---
title: Getting Started
---

# Quick Start

Mophidian provides a cli tool called `moph` to streamline the creation of your website. To start you will want to create a new mophidian project. If you ever want to know what a command does or to know what is possible, use `moph --help` or `moph {command} --help`

For more on the cli tool see the [cli](/docs/cli/) section.

## Creating a Project

```bash
moph new {project name}
```

This will create the project in a new directory with the same name as the project name. Mophidian has also has a preset with a page, layout, and a component. This is a good option if you want an example of how a project can be structured. To use the preset use;

```bash
moph new {project name} -p|--preset
```

## Development

Now that you have a project you can begin creating your website. The file structure is based on the [svelte kit](https://kit.svelte.dev/docs/advanced-routing) file structure. Each page is in it's own directory and each directory only has one layout. These are the only two pages that have limits per directory. You may write as many static and markdown files in these directories as you want.

You may have noticed that markdown was mentioned. Each markdown file in the source directory, `src/pages` by default, will be rendered to html. Markdown files use the closest layout file as it's base.

Since Mophidian is a route based SSG, each page is an `index.html` file is in it's own directory. There can be multiple markdown files in one directory, so how does that fit into this? Well each markdown files get their own directory equal to the name of the file. `README` markdown files are treated as `index.html` so be careful when placing page and markdown files in the same directory.

You may only have one `page.phml` and `layout.phml` file per directory. `page.phml` files look like this.

```html
<!-- page.phml -->

<>
    {Your content here}
</>

<!--       or       -->

<{html-tag}>
    {Your content here}
</{html-tag}>
```

while `layout.phml` pages are similar they will require a `<Slot />` tag. They will look like this.

```html
<!-- layout.phml -->

<>
    {Your content here}
    <Slot />
    {Your content here}
</>

<!--       or       -->

<{html-tag}>
    {Your content here}
    <Slot />
    {Your content here}
</{html-tag}>
```

Markdown files are normal markdown files but you may also have frontmatter/metadata. The frontmatter should be written in yaml. This data is exposed to the layouts on page render.

```markdown
---
title: Sample Page Title
pubDate: Thu, 23 May 2023 UTC
tags:
    - sample
    - docs
    - getting_started

---

# Sample Page

Some content here
```

There are also components which are in the `src/components` directory by default. They are structure just like the `page.phml` file. After creating a component it's filename and path are used to create the associated element tag which can be used in any `page.phml`, `layout.phml`, markdown, and other component files. All sub directories leading to the component are used in the name and are separated with a `.`. So if you have a component file named `Sample.phml` you will get a `<Sample>` tag to use in all other files. If you have a component file `nav/Navbar.phml` you will get a `<Nav.Navbar />` tag to use in all other files. If you want to use the component like a normal element and not just a self closing element you can add a `<Slot />` element where you want all the children to be placed in the component. To see more on how components work, it is recommended to read up on the [phml docs](https://example.com) as phml's default component system is what is used here in Mophidian.

It may be easier to have more of an example. Suppose you have the file structure of

```plaintext
src/
├ components/
│ └ Sample.phml
└ pages/
  ├ page.phml
  ├ layout.phml
  └ Sample.md
```

With the files containing
```html
<!-- Sample.phml -->

<div>Component</div>
```

```html
<!-- layout.phml -->

<>
    <h3>Header</h3>
    <Slot />
</>
```

```html
<!-- page.phml -->

<>
    <h1>Home</h1>
    <Sample />
<>
```

```markdown
# Sample markdown page

Page content
```

With each page inheriting from it's corresponding layout you get a built output that has the structure of

```plaintext
out/
├ index.html
└ Sample
  └ index.html
```

and file with the contents of

```html
<!-- out/index.html -->

<!DOCTYPE html>
<html>
    <head>
        ... <!-- See rendering section -->
    </head>
    <body>
        <h3>Header</h3>
        <h1>Home</h1>
        <div>Component</div>
    </body>
</html>
```

```html
<!-- out/Sample/index.html -->

<!DOCTYPE html>
<html>
    <head>
        ... <!-- See rendering section -->
    </head>
    <body>
        <h3>Header</h3>
        <article>
            <h1>Sample markdown page</h1>
            <p>Page content</p>
        </article>
    </body>
</html>
```

To view your changes in real time use `moph serve` and if you want to preview your changes you can use `moph preview`. To automatically open the website in a browser you may use the `-o|--open` flag.

To find out more about how the file structure works see the [File System](/docs/file-system/) section.

## Building

To build you project you use `moph build`. This will incrementally build your site. This means if a rendered output of a page is the same as what was generated in the previous call of `moph build`, the page will be skipped. You may bypass this feature with the `--dirty` flag.

By default the built/rendered files will be output to the `out/` directory. These files are what you upload to your choice of site hosting.

## Summary

Use `moph new {project name}` to create a new project. Fill your newly creating project with `page.phml`, `layout.phml`, and markdown files. Then build your site with `moph build`.

To learn more about the in depth features of mophidian please read the rest of the documentation.
