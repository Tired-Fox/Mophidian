"""Installation using setup.py is deprecated.
Use `python(3) -m pip install .` instead to use pyproject.toml
"""

import sys

from setuptools import setup

sys.exit(__doc__)

# This is read by github so it still thinks of it as a package
setup(
    name="mkdocs"
)