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
    ~core.QtCore
    ~core.QtGui

"""

from . import common
from .core import Variable, componentsList, Component, QtGui, QtCore
from .variable_choose import VariableChoose

