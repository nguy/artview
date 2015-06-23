# add this folder to path so I can import artview
import sys
import os
path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

import artview

from parser import parse
DirIn, field = parse(sys.argv)
artview.run(DirIn, field)
