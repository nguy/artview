"""
radar_and_grid.py

Driver function that creates two ARTView displays. The first
a native radar coordinate display, the second a grid display.
"""
import os
import sys

from ..core import Variable, QtGui, QtCore
from ..components import RadarDisplay, GridDisplay, Menu
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for radar and grid display
    """
    DirIn = _parse_dir(DirIn)

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    menu = Menu(DirIn, filename, mode=("Radar", "Grid"), name="Menu")
    Vradar = menu.Vradar
    Vgrid = menu.Vgrid

    field = _parse_field(Vradar.value, field)

    # start Displays
    plot1 = RadarDisplay(Vradar, Variable(field), Variable(0),
                         name="Radar", parent=menu)
    plot2 = GridDisplay(Vgrid, Variable(field), Variable(0),
                        name="Grid", parent=menu)

    # start program
    app.exec_()
