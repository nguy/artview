"""
================================
Plugings (:mod:`artview.plugins`)
================================

.. currentmodule:: artview.plugins

ARTview offer some function to start programs using basic configurations.

.. autosummary::
    :toctree: generated/

    exemple1
    exemple2
"""


import os
import sys

thismodule = sys.modules[__name__]
_plugins = []

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    tmp = __import__(module[:-3], locals(), globals())
    for plugin in tmp._plugins:
        setattr(thismodule, module[:-3], plugin)
        _plugins.append(plugin)

del module
del os
del sys
del thismodule
del tmp
del plugin
