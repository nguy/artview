"""
================================
Plugins (:mod:`artview.plugins`)
================================

.. currentmodule:: artview.plugins

ARTview offer some function to start programs using basic configurations.

.. autosummary::
    :toctree: generated/

"""


import os
import sys

thismodule = sys.modules[__name__]
_plugins = []

for module in os.listdir(os.path.dirname(__file__)):
    if module.startswith('_') or module[-3:] != '.py':
        continue
    tmp = __import__(module[:-3], locals(), globals())
    for plugin in tmp._plugins:
        setattr(thismodule, plugin.__name__, plugin)
        _plugins.append(plugin)
        #update docstring to add plugin
        __doc__ = __doc__ + """    %s\n""" % plugin.__name__

del module
del os
del sys
del thismodule
del tmp
del plugin


