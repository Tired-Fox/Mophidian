# Getting Started

## Basics

A website can be as simple as adding html and or markdown files to the pages directory and building the project. Additionally, you may add CSS files to either the `pages/` directory or the `static/` directory. All static files, non html and markdown files, will be kept as is in the location you put them, so feel free to organize your files how you like.

You can look at the [Template Design]() documentation for Jinja2 templating as that is what is used in Mophidian html files. You may create Jinja2 flavored html files in the `layouts/` directory to make layouts along with the `components/` directory to make components. The idea being a layout is a full page that takes a type of slot that can be used to hold a sub pages content. A component is a reusable chunk of html that you want to repeat. Make sure to read the [docs](https://tired-fox.github.io/Mophidian/docs/) and [blog](https://tired-fox.github.io/Mophidian/blog/) for Mophidian to see examples of how layouts, components, and jinja2 templating fit into the development process.

## Integrations

If you would like to use things like SASS or Tailwindcss you could always add them yourself using node. Or, you could use Mophidians built in integration system. Right now Mophidian only support SASS and Tailwind, but that could prove usefull. 

With the SASS integration you may put sass files either anywhere in the pages directory or you may put them in the `styles/` directory. In either location they will be compiled to their corresponding CSS file. SASS files in the `pages/` directory will retain their relative path while files in the `styles/` directory will be translated to a `site/css/` folder.

The Tailwindcss integration will automatically set up the `tailwind.config.js` file and the tailwind.css file. When the integration is enabled it will run a tailwind command to check all compiled html files for tailwind styling. It will then compile a tailwind.min.css file in the `site/css/` directory.

## Available Data

Mophidian exposes data from the build process to each template allowing for the user to access it. It gives access to markdown metadata, layouts, components, config variables, navigation data, table of contents data, and page data. Each of which can be very useful for building your site.

Look at the Mophidian [docs](https://tired-fox.github.io/Mophidian/docs/) to see more about how to use this data.

## Deploying

When building the compiler will look at the provided website root and expose important information as needed. For example if you plan to host your site on github pages, your site will be hosted in a sub directory to the root directory of the host. So, you can provide a variable in the config to specify the root. This is useful since Mophidian will then give you access to this root variable for links.

Here is a list of what this provides:

* Relative markdown links
* Access to the `site.root` variable in template files.
  * Can access files such as `/{{ site.root }}/css/tailwind.min.css`
* Additionally you can toggle a flag and the compiler will build the website in that subdirectory.

If you don't have a subdirectory and are hosting the website at the root level, you can use normal file base routing such as `/css/tailwind.min.css` or `/`

Mophidian uses a lot of default markdown plugins to give the a great markdown experience out of the box. If you wish to add more plugins you can look at the [built in plugins](https://python-markdown.github.io/extensions/) with the python [markdown](https://python-markdown.github.io/) plugin. Additionally, I recommend using plugins from [PyMdown](https://facelessuser.github.io/pymdown-extensions/). You may also follow the [extensions api](https://python-markdown.github.io/extensions/api/) to making your own plugin if you wish to do so.

When you are ready to build your site you may use the `mophidian build` command to do so. This will create a `site/` directory, by default, and place all your compiled files and static files in here as if it was the root directory of your host.

[**Home**](/)