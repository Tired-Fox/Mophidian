from core import get_files, File, Page, get_navigation
from core.config import Config

if __name__ == "__main__":
    cfg = Config()
    pages, content = get_files(cfg)

    get_navigation(pages, content, cfg)
