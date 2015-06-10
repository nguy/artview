"""
===========================================
Main Components (:mod:`artview.components`)
===========================================

.. currentmodule:: artview.components

ARTview offer some basic Components for visualisation of data using Py-ART.

.. autosummary::
    :toctree: generated/

    Display
    Menu
    TiltButtonWindow
    FieldButtonWindow
"""

from .plot import Display
from .menu import Menu
from .tilt import TiltButtonWindow
from .field import FieldButtonWindow
from .component_control import ComponentsControl
