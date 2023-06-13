from tcfg import cfg, new, PathType

class Paths(cfg):
    files: PathType = new("src/pages")
    """Where the main pages for the website are located."""
    public: PathType = new("src/public")
    """Where public/static files are located."""
    components: PathType = new("src/components")
    """Where component files are located."""
    scripts: PathType = new("src/scripts")
    """Where python script files are located."""
    out: PathType = new("out")
    """Where the built files will be written."""

class Site(cfg):
    site_name: str
    """Website name. This is exposed to the compiler."""

    uri: PathType
    """Base website path. For example if you plan to deploy to github pages,
    you will have to use the project name as the base folder of the website.
    Ex: `/<project/`. Slashes are optional, but this will be used while compiling
    urls inside the website.
    """

class Config(cfg):
    """Mophidian configuration."""
    _path_ = "src/moph.yml"

    paths: Paths
    """Paths for different file system operations."""
    site: Site
    """General site settings. These are exposed to the phml compiler."""
