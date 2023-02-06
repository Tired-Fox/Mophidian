from re import match
from pathlib import Path
import time

from teddecor import TED, Logger
from phml import PHML, Formats

from mophidian import CONFIG
from mophidian.file_system import Directory, Component, Nav, Static, Layout, Page, Markdown, Renderable
from mophidian.core.util import REGEX, PAGE_IGNORE
from datetime import datetime

__all__ = [
    "construct_components",
    "construct_static",
    "construct_file_system",
    "generate_sitemaps",
    "generate_rss"
]

class SitemapUrl:
    """Represents a url/link in a sitemap."""
    def __init__(self, loc: str, last_mod: float) -> None:
        self.loc = Path(CONFIG.site.base_url).joinpath(loc.lstrip("/"), "index.html").as_posix()
        self.last_mod = datetime.fromtimestamp(float(last_mod)).strftime("%Y-%m-%dT%H:%M:%S")
        self.priority = None


class RSSImage:
    """Represents a rss channel image."""
    def __init__(self, title: str, url: str, width: int, height: int) -> None:
        self.title = title
        self.url = url
        self.width = width or 31
        self.height = height or 88

    def __repr__(self) -> str:
        return f"RSSImage(title: {self.title!r}, url: {self.url!r}, \
dim: ({self.width}, {self.height}))"

class RSSItem:
    """Represents a rss channel item."""
    def __init__(self, title: str, url: str, description: str, pub_date: str) -> None:
        dt_format = "%a, %d %b %Y %H:%M:%S %Z"
        self.title = title
        self.url = url
        self.description = description
        try:
            self.pub_date = datetime.strptime(pub_date, dt_format).strftime(dt_format)
        except Exception:
            self.pub_date = datetime.now().astimezone().strftime(dt_format)

    def __repr__(self) -> str:
        return f"RSSItem(title: {self.title!r}, url: {self.url!r}, pubDate: {self.pub_date})"

def construct_components(path: str) -> Directory:
    """Find all the components in the given path and construct a file structure."""

    components = Directory(path)
    for file in Path(path).glob("**/*.*"):
        if file.suffix == ".phml":
            components.add(Component(file.as_posix(), path))
        else:
            suggestion = f"{TED.parse(f'[@Fred]{file.suffix}')} to {TED.parse('[@Fgreen].phml')}"
            Logger.Debug(
                "Invalid component:",
                f"{TED.parse(f'[@Fyellow]{TED.escape(file.as_posix())}')}.",
                "Try changing",
                suggestion,
                label="Debug.[@Fred]Error[@]"
            )
    return components

def construct_static(path: str) -> Directory:
    """Find all the static files in the given path and construct a file structure."""

    static_files = Directory(path)
    for file in Path(path).glob("**/*.*"):
        static_files.add(Static(file.as_posix(), path))

    return static_files

def construct_file_system(path: str) -> tuple[Directory, Nav]:
    """Find all the files in the given path and construct a file structure."""

    root = Directory(path)
    for _file in Path(path).glob("**/*.*"):
        # Pages and Layouts
        if _file.suffix == ".phml":
            if REGEX["layout"]["name"].match(_file.name) is not None:
                root.add(Layout(_file.as_posix(), path))
            elif REGEX["page"]["name"].match(_file.name) is not None:
                root.add(Page(_file.as_posix(), path))
            else:
                file_info = REGEX["file"]["name"].search(_file.name)
                file_name, _, _, _ = (
                    file_info.groups() if file_info is not None else ("", None, None, "")
                )
                if file_name in PAGE_IGNORE:
                    root.add(Page(_file.as_posix(), path))

        # Markdown files
        elif _file.suffix in [".md", ".mdx"]:
            root.add(Markdown(_file.as_posix(), path))

        # Static files
        else:
            root.add(Static(_file.as_posix(), path))

    root.build_hierarchy()
    nav = root.build_nav()
    return root, nav


# * => .*
# ** => (.*/?)*
def format_pattern(pattern: str) -> str:
    tokens = pattern.replace("\\", "/").split("/")
    result = []
    for p in tokens:
        if p == "**":
            result.append("(.*/?)*")
        elif p == "*":
            result.append("(.*)")
        else:
            result.append(p)
    return "/".join(result)

def sitemap_name(pattern: str) -> str:
    tokens = pattern.replace("\\", "/").split("/")
    result = []
    for p in tokens:
        if p.strip() not in ["*", "**", ""]:
            result.append(p)
    return "_".join([*result, "sitemap.xml"])

def patterned_sitemaps(file_system: Directory):
    phml = PHML()
    indexes = []
    for pattern in CONFIG.build.sitemap.patterns:
        dest_path = Path(CONFIG.site.dest).joinpath("sitemaps", sitemap_name(pattern))
        indexes.append(SitemapUrl(
            (
                Path(CONFIG.site.root)
                    .joinpath("sitemaps", sitemap_name(pattern))
                    .as_posix()
            ), 
            time.time()
        ))
        pattern = format_pattern(pattern)
        matches = []
        for file in file_system.renderable():
            if match(pattern, file.relative_url):
                matches.append(SitemapUrl(file.url, file.epoch))
                file_system.remove(file.full_path)

        #! WARNING: Do not parse xml files as html in phml. This will override a lot of security
        #! and shoud not be done with any untrusted xml files.
        phml.load(
            Path(__file__).parent.parent.parent.joinpath("presets/sitemap.xml"), 
            from_format=Formats.HTML
        )
        phml.write(dest_path, file_type=Formats.XML, urls=matches)
        
    # Generating sitemap index file and adding it to a robots.txt file
    #! Warning: Again do not replicate parsing xml files as html. This bipasses many security
    #! checks. 
    phml.load(
        Path(__file__).parent.parent.parent.joinpath("presets/sitemapindex.xml"),
        from_format=Formats.HTML,
        auto_close=False
    )
    sitemap_index = Path(CONFIG.site.dest).joinpath("sitemap.xml")
    phml.write(
        sitemap_index,
        file_type=Formats.XML,
        indecies=indexes
    )
    
    with open(Path(CONFIG.site.dest).joinpath("robots.txt"), "+w", encoding="utf-8") as robots:
        robots.write(f"Sitemap: {Path(CONFIG.site.base_url).joinpath('sitemap.xml').as_posix()}")

def generate_sitemaps(file_system: Directory):
    if len(CONFIG.build.sitemap.patterns) > 0:
        patterned_sitemaps(file_system)
    else:
        phml = PHML()
        matches = [
            SitemapUrl(file.url, file.epoch)
            for file in file_system.files()
            if isinstance(file, Renderable)
        ]
        
        phml.load(
            Path(__file__).parent.parent.parent.joinpath("presets/sitemap.xml"),
            from_format=Formats.HTML,
            auto_close=False
        )

        phml.write(
            Path(CONFIG.site.dest).joinpath("sitemap.xml"),
            file_type=Formats.XML,
            urls=matches
        )
        
        with open(Path(CONFIG.site.dest).joinpath("robots.txt"), "+w", encoding="utf-8") as robots:
            robots.write(f"Sitemap: {Path(CONFIG.site.base_url).joinpath('sitemap.xml').as_posix()}")
            
def generate_rss(file_system: Directory):
    if len(CONFIG.build.rss.paths) > 0:
        items = []
        paths = [path.strip("/") for path in CONFIG.build.rss.paths]
        for file in file_system.markdown():
            if any(path in file.path for path in paths):
                items.append(RSSItem(
                    file.title, 
                    Path(CONFIG.site.base_url).joinpath(file.url.strip("/")).as_posix(), 
                    file.locals.pop("description", ""), 
                    file.locals.pop("pub_date", None) or file.locals.pop("pubDate", None)
                ))

    else:
        items = []
        for file in file_system.markdown():
            items.append(RSSItem(
                    file.title or CONFIG.site.name,
                    Path(CONFIG.site.base_url).joinpath(file.url.strip("/")).as_posix(), 
                    file.locals.pop("description", ""), 
                    file.locals.pop("pub_date", None) or file.locals.pop("pubDate", None)
            ))
    
    image_cfg = CONFIG.build.rss.image
    image = RSSImage(
        image_cfg.title,
        image_cfg.url,
        image_cfg.width,
        image_cfg.height,
    ) if image_cfg.url != "" else None

    phml = PHML()

    phml.load(
        Path(__file__).parent.parent.parent.joinpath("presets/feed.xml"),
        from_format=Formats.HTML,
        auto_close=False
    )

    phml.write(
        Path(CONFIG.site.dest).joinpath("feed.xml"),
        file_type=Formats.XML,
        image=image,
        items=items,
        feed_link=Path(CONFIG.site.base_url).joinpath(CONFIG.site.root, "feed.xml"),
        site_link=Path(CONFIG.site.base_url).joinpath(CONFIG.site.root),
        site_description=CONFIG.site.description,
        language=CONFIG.build.rss.language,
    )
