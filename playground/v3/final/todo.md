- [x] global variable for creating url with website root inserted to beginning.
- [x] Automatically rip `head` element from `pages`, `layouts`, and `components` and append there children to root templates `head`
- [x] Route all files as any file name -> index.html or have special file names that stay as is in their current directory
- [x] Generate page title from file name
  - [x] `tokanize_name` from phml
  - [x] Title case the title
- [x] Get page by path
- [ ] Generate site nav
  - [ ] Full nav tree
  - [ ] Each page's next and previous
- [ ] Generate TOC from markdown file
- [ ] favicon through config and head link tag
- [ ] when copying elements from page head to base head, don't duplicate tags
- [ ] Dynamic routes
  - [ ] dynamic route generation through python element
  - [ ] Generates from `content/` directory
  - [ ] `...dir` recursive catch all
  - [ ] `dir` catch all
  - [ ] `slug` file used for desired output else relevant `layout.phml` will be used.
  - [ ] `page.phml` and `layout.phml` will be given data about all the pages found for the catch all
- [ ] Auto add website root to urls
- [ ] Integrations
  - [ ] Tailwind
  - [ ] Sass

```html
<!DOCTYPE html>
<html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/x-icon" href="/static/error.png">
        <link rel="stylesheet" href="{url_for('static', filename='style.css')}">
        <title>{error}</title>
    </head>
    <style>
        @import url("https://fonts.googleapis.com/css?family=Poppins:400");
        body {
            font-family: "Poppins", sans-serif;
            background-color: #282a3a;
            color: #dcd7c9;
        }
        #error-code {
            color: #E94560;
        }
    </style>
    <body>
        <div class="flex flex-col items-center justify-center h-100">
            <h1><span id="error-code">404</span> Not Found</h1>
            <p>Oops it looks like the page you are trying to reach doesn't exist</p>
            <a class="mt-2" href="/Mophidian/">Back to Home</a>
        </div>
    </body>

</html>\
```