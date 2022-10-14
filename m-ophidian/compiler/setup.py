import os
import shutil

def init_static():
    '''Remove old files from site folder. Then copy all static files to `site/`'''
    if os.path.isdir('site/'):
        shutil.rmtree('site/')
    if os.path.isdir('static/'):
        shutil.copytree('static/', 'site/')