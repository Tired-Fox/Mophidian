import markdown
import json

with open('config.json', 'r', encoding='utf-8') as config_file:
    cfx = json.load(config_file)

with open('sample.md', 'r', encoding='utf-8') as mark_file:
    content = mark_file.read()

md = markdown.Markdown(extensions=cfx["markdown"]["extensions"], extension_configs=cfx["markdown"]["extension_configs"])

html = md.reset().convert(content)

with open('sample.html', '+w', encoding="utf-8") as html_file:
    html_file.write(f'''\
<!DOCTYPE html>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Document</title>
</head>
<body>
    {html}
</body>
</html>\
''')
