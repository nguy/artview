"""
==========================
Core (:mod:`artview.core`)
==========================

.. currentmodule:: artview.core

ARTview is based in the abstract Component class and shared Variables.

.. autosummary::

    :toctree: generated/

    ~core.Variable
    ~core.Component
    ~PyQt4.QtCore
    ~PyQt4.QtGui

"""

from . import common
from .core import Variable, componentsList, Component, QtWidgets, QtCore, QtGui
from .variable_choose import VariableChoose
