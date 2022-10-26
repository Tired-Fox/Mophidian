from sys import path

path.insert(0, '../config')
path.insert(0, '../')

from .pages import pages
from .build import Build
