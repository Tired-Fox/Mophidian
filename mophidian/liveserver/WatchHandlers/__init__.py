from .Content import WatchContent
from .Pages import WatchPages
from .Static import WatchStatic

import sys        
 
# appending the directory of mod.py
# in the sys.path list
sys.path.append('../../compiler/')  

all = [
    "WatchContent",
    "WatchPages",
    "WatchStatic",
]