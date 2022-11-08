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

* `Blank` - The minimal default template (Currently the only option)
* `Docs` - A documentation centric template
* `Blog` - A blogging centric template

Don't forget to check out the website [**blog/snippets/**](/Mophidian/blog/snippets/) page to see code snippets of common things such as navigation, table of contents, styling for markdown, etc.