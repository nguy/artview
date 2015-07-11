"""
================================
Scripts (:mod:`artview.scripts`)
================================

.. currentmodule:: artview.scripts

ARTview offer some function to start programs using basic configurations.

.. autosummary::
    :toctree: generated/

"""

import os
import sys

thismodule = sys.modules[__name__]
scripts = {}

for module in os.listdir(os.path.dirname(__file__)):
    if module.startswith("_") or module[-3:] != '.py':
        continue
    tmp = __import__(module[:-3], locals(), globals())
    try:
        scripts[module[:-3]] = tmp.run
        setattr(thismodule, module[:-3], tmp.run)
        #update docstring to add plugin
        __doc__ = __doc__ + """    %s\n""" % module[:-3]
    except:
        pass


del module
del os
del sys
del thismodule
del tmp

