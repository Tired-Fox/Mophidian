import os
import shutil
from pathlib import Path

from .pages import Page, Pages

from pprint import pprint  #! DEBUG ONLY


def init_static():
    '''Remove old files from site folder. Then copy all static files to `site/`'''
    if os.path.isdir('site/'):
        shutil.rmtree('site/')
    if os.path.isdir('static/'):
        shutil.copytree('static/', 'site/')


# Filesturture looks like this
# {index,readme}.{html.md}
#   - [dir]
#       - {index,readme}.{html,md}
def find_pages():
    print("Finding pages...")

    if os.path.isdir('pages'):
        pages = Pages()
        page_list = []
        for path in Path('pages').glob(f"./**/*.*"):
            if path.suffix in [".md", ".html"]:
                pages.append(Page(path.parent.as_posix(), path.name, path.suffix))

        print(pages)
        # del pages['about/license/MIT']
        print(pages[1:3])
