"""
===========================================
Main Components (:mod:`artview.components`)
===========================================

.. currentmodule:: artview.components

ARTview offers some basic Components for visualization 
of weather radar data using Py-ART and
ARTview functions.

.. autosummary::
    :toctree: generated/

    RadarDisplay
    GridDisplay
    Menu
    LevelButtonWindow
    FieldButtonWindow
    LinkPlugins
    SelectRegion
    PlotDisplay
"""

from .plot_radar import RadarDisplay
from .plot_grid import GridDisplay
from .menu import Menu
from .level import LevelButtonWindow
from .field import FieldButtonWindow
from .component_control import LinkPlugins
from .select_region import SelectRegion
from .plot_simple import PlotDisplay
