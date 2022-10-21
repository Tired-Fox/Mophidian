snippets = {
    "starter_index": '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mophidian</title>
</head>
<style>
    * {
        box-sizing: border-box;
    }
    
    body {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .box {
        padding: 1rem;
        border-size: 1px;
        border-style: solid;
        border-color: black;
        width: fit-content;
    }
</style>
<body>
    <div class="box">
        <h1>Hello and welcome to Mophidian, a SSG made in python.</h1>
        <h3>My goal is to make something that is easy to use, but also gives you as many features as possible.</h3>
        <p>
            <a href="https://github.com/Tired-Fox/Mophidian" class="underline">
                Please checkout my github to see the current status of the project.
            </a>
        </p>
    </div>
</body>
</html>\
''',
    "tailwind_config_open": '''\
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["site/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [\n\
''',
    "tailwind_config_close": '''\
  ],
}\
''',
    "tailwind_css": """\
@tailwind base;
@tailwind components;
@tailwind utilities;\
""",
    "tailwind_scripts": {
        "tailwind": "tailwindcss -i ./styles/tailwind.css -o ./static/tailwind.css",
        "tailwind:mini": "tailwindcss -i ./styles/tailwind.css -o ./static/tailwind.min.css --minify",
        "tailwind:watch": "tailwindcss -i ./styles/tailwind.css -o ./static/tailwind.css --watch",
    },
    "sass_scripts": {
        "css": "sass styles:static/css",
        "css:watch": "sass --watch styles:static/css",
        "css:compress": "sass --style=compressed styles:static/css",
        "css:watch:compress": "sass --watch --style=compressed styles:static/css",
    },
    "integration_file_structure": '''
project
project
├ components/
├ content/
├ layouts/
├ styles/
│ └ tailwind.css (optional)
├ pages/
│ └ index.html
└ static/\
''',
    "base_file_structure": '''
project
project
├ components/
├ content/
├ layouts/
├ pages/
│ └ index.html
└ static/\
''',
}
