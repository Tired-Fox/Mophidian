from .setup import init_static, find_pages, get_components, get_layouts
from config import Config

from pprint import pprint


def full():
    # config = Config()
    # init_static()
    pages = find_pages()
    components = get_components()
    layouts = get_layouts()

    print([page.uri for page in pages])
    pprint(components)
    pprint(layouts)
    pass
