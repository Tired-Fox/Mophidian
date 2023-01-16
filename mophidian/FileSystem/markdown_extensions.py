import functools
import os
from pathlib import Path
import posixpath
from urllib.parse import urlsplit, urlunsplit, unquote

from markdown import Markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import AMP_SUBSTITUTE
from xml.etree.ElementTree import Element

from teddecor import Logger

@functools.lru_cache(maxsize=None)
def _norm_parts(path: str) -> list[str]:
    if not path.startswith('/'):
        path = '/' + path
    path = posixpath.normpath(path)[1:]
    return path.split('/') if path else []

def get_relative_url(url: str, other: str) -> str:
    """
    Return given url relative to other.
    Both are operated as slash-separated paths, similarly to the 'path' part of a URL.
    The last component of `other` is skipped if it contains a dot (considered a file).
    Actual URLs (with schemas etc.) aren't supported. The leading slash is ignored.
    Paths are normalized ('..' works as parent directory), but going higher than the
    root has no effect ('foo/../../bar' ends up just as 'bar').
    """
    # Remove filename from other url if it has one.
    dirname, _, basename = other.rpartition('/')
    if '.' in basename:
        other = dirname

    other_parts = _norm_parts(other)
    dest_parts = _norm_parts(url)
    common = 0
    for a, b in zip(other_parts, dest_parts):
        if a != b:
            break
        common += 1

    rel_parts = ['..'] * (len(other_parts) - common) + dest_parts[common:]
    relurl = '/'.join(rel_parts) or '.'
    return relurl + '/' if url.endswith('/') else relurl

def url_relative_to(current: str, other: str) -> str:
    """Return url for file relative to other file."""
    return get_relative_url(current, other)

class _RelativePathTreeprocessor(Treeprocessor):
    def __init__(self, file, files) -> None:
        self.file = file
        self.files = files

    def run(self, root: Element) -> Element:
        """
        Update urls on anchors and images to make them relative
        Iterates through the full document tree looking for specific
        tags and then makes them relative based on the site navigation
        """
        for element in root.iter():
            if element.tag == 'a':
                key = 'href'
            elif element.tag == 'img':
                key = 'src'
            else:
                continue

            url = element.get(key)
            assert url is not None
            new_url = self.path_to_url(url)
            element.set(key, new_url)

        return root

    def path_to_url(self, url: str) -> str:
        scheme, netloc, path, query, fragment = urlsplit(url)

        if (
            scheme
            or netloc
            or not path
            or url.startswith('/')
            or url.startswith('\\')
            or AMP_SUBSTITUTE in url
            or '.' not in os.path.split(path)[-1]
        ):
            # Ignore URLs unless they are a relative link to a source file.
            # AMP_SUBSTITUTE is used internally by Markdown only for email.
            # No '.' in the last part of a path indicates path does not point to a file.
            return url

        # Determine the filepath of the target.
        target_uri = posixpath.join(posixpath.dirname(self.file.src), unquote(path))
        target_uri = posixpath.normpath(target_uri).lstrip('/')

        # Validate that the target exists.
        target_file = self.files.find(target_uri)

        if not Path(target_uri).exists() and target_file is None:
            Logger.warning(
                f"Page '{self.file.relative_url}' contains a link to "
                f"'{target_uri}' which is not found in the files."
            ).flush()
            return url

        if target_file is not None:
            path = url_relative_to(target_file.relative_url, self.file.relative_url)
        else:
            path = url_relative_to(target_uri, self.file.relative_url)

        components = (scheme, netloc, path, query, fragment)
        return urlunsplit(components)

class _RelativePathExtension(Extension):
    """
    The Extension class is what we pass to markdown, it then
    registers the Treeprocessor.
    """

    def __init__(self, file, files) -> None:
        self.file = file
        self.files = files

    def extendMarkdown(self, md: Markdown) -> None:
        relpath = _RelativePathTreeprocessor(self.file, self.files)
        md.treeprocessors.register(relpath, "relpath", 0)