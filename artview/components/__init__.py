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
import pyart
from pkg_resources import parse_version

from .plot_radar import RadarDisplay
if parse_version(pyart.__version__) >= parse_version('1.6.0'):
    from .plot_grid import GridDisplay
else:
    from .plot_grid_legacy import GridDisplay
from .plot_points import PointsDisplay
from .menu import Menu
from .level import LevelButtonWindow
from .field import FieldButtonWindow
from .component_control import LinkPlugins
from .select_region import SelectRegion as SelectRegion_dev
from .select_region_old import SelectRegion
from .plot_simple import PlotDisplay

del pyart
del parse_version