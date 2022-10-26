from core import get_files, File, Page, get_navigation
from core.config import Config

if __name__ == "__main__":
    cfg = Config()
    files, content = get_files(cfg)

    nav = get_navigation(files, content, cfg)
    files.build_all_sass(cfg)
    files.copy_all_static()
