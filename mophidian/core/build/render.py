from pathlib import Path
from shutil import rmtree
from os import remove
import string
import time

from phml import PHML

from mophidian import states, CONFIG
from mophidian.core.util import title, url
from mophidian.file_system import (
    Directory,
    Nav,
    FileState,
    File
)


__all__ = [
    "render_pages",
    "write_static_files"
]

_SCRIPT_TEMPLATE_STR = """
<script defer>
    var livereload = function(version) {
        var req = new XMLHttpRequest();
        req.onloadend = function() {
            if (parseFloat(this.responseText) > version) {
                location.reload();
                return;
            }
            var launchNext = livereload.bind(this, version);
            if (this.status === 200) {
                launchNext();
            } else {
                setTimeout(launchNext, 3000);
            }
        };
        req.open("GET", '/livereload/${version}/${path}');
        req.send();
    }
    livereload(${version});
    console.warn('[Mophidian] Enabled live reload: ', "/livereload/${version}/${path}");
</script>
"""
_SCRIPT_TEMPLATE = string.Template(_SCRIPT_TEMPLATE_STR)



def is_file_different(file: File, source_data: str) -> bool:
    try:
        with open(file.dest(states["dest"]), "r", encoding="utf-8") as dest:
            dest_data = dest.read()

        return source_data != dest_data
    except Exception:
        return True
    
def is_static_different(file: File) -> bool:
    try:
        with open(file.full_path, "r", encoding="utf-8") as source:
            source_data = source.read()
        with open(file.dest(states["dest"]), "r", encoding="utf-8") as dest:
            dest_data = dest.read()

        return source_data != dest_data
    except Exception:
        return True

def render_pages(
    root: Directory,
    static_files: Directory,
    component_files: Directory,
    out: str,
    phml: PHML,
    nav: Nav = Nav(""),
    *,
    dirty: bool = False,
    live_reload: bool = False
):
    """Render all the pages with their layouts to their destination file."""

    global_vars = {
        "url": url,
        "title_case": title,
        "nav": nav,
    }

    epoch = time.time()
    # Render pages
    for page in root.renderable():
        if page.state == FileState.UPDATED:
            page_vars = {
                "title": page.title
            }

            if CONFIG.build.rss:
                page_vars["rss_feed"] = Path(CONFIG.site.base_url).joinpath(CONFIG.site.root, "feed.xml").as_posix()
            
            # Ensure path to file
            page.dest(out).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            dest = Path(page.dest(out))
            output = page.render(
                phml,
                page_files=root,
                static_files=static_files,
                component_files=component_files,
                **page_vars,
                **global_vars
            )

            if live_reload:
                output += f'\n{_SCRIPT_TEMPLATE.substitute(version=int(epoch), path=page.full_path)}'

            if is_file_different(page, output) or dirty:
                # Update page epoch
                page.epoch = epoch
                with open(dest, "+w", encoding="utf-8") as file:
                    file.write(output)
            page.state = FileState.NULL # Set state as up to date and doesn't need to be rendered
        elif page.state == FileState.DELETED:
            dest = Path(page.dest(out))
            root.remove(page.full_path)
            page.delete()
            if len(list(dest.parent.glob("**/*.*"))) == 1:
                rmtree(dest.parent)
            elif dest.is_file():
                remove(dest)

def write_static_files(root: Directory, static: Directory, out: str, dirty: bool = False):
    """Write static files to their destination."""

    # static files found in the pages directory
    for file in root.static():
        if (
            (
                file.state == FileState.UPDATED
                and is_static_different(file)
            )
            or (
                dirty
                and file.state != FileState.DELETED
            )
        ):
            file.write(out)
        elif file.state == FileState.DELETED:
            dest = file.dest(out)
            root.remove(file.full_path)
            if len(list(dest.parent.glob("**/*.*"))) == 1:
                rmtree(dest.parent)
            else:
                remove(dest)

    # static files in the static directory
    for file in static.static():
        if file.state == FileState.UPDATED:
            file.write(out)
        elif file.state == FileState.DELETED:
            dest = file.dest(out)
            static.remove(file.full_path)
            if len(list(dest.parent.glob("**/*.*"))) == 1:
                rmtree(dest.parent)
            else:
                remove(dest)


