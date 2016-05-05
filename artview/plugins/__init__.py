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
_plugins = {}
_modes = []

for module in os.listdir(os.path.dirname(__file__)):
    if module.startswith('_') or module[-3:] != '.py':
        continue
    if sys.version_info[0] < 3:
        tmp = __import__(module[:-3], locals(), globals())
    else:
        import importlib
        tmp = importlib.import_module('.'+module[:-3], __package__)
    for plugin in tmp._plugins:
        setattr(thismodule, plugin.__name__, plugin)
        _plugins[plugin.__name__] = plugin
        # update docstring to add plugin
        __doc__ = __doc__ + """    %s\n""" % plugin.__name__
    if hasattr(tmp,'_modes'):
        _modes += tmp._modes

del module
del os
del sys
del thismodule
del tmp
del plugin
