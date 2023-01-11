from config import CONFIG

def url(url: str) -> str:
    """Construct a url given a page url and the project's rool."""

    root = f"/{CONFIG.site.root.strip('/')}/" if CONFIG.site.root != "" else ""
    return root + url.lstrip("/")
