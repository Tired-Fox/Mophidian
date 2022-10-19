snippets = {
    "tailwind_config": '''\
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["site/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [],
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
}
