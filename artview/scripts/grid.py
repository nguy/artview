"""
grid.py

Driver function that creates an ARTView display for gridded radar data.
"""
import os
import sys

from ..core import Variable, QtGui, QtCore
from ..components import GridDisplay, Menu
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for simple grid display
    """
    DirIn = _parse_dir(DirIn)

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    menu = Menu(DirIn, filename, mode=("Grid",), name="Menu")
    Vgrid = menu.Vgrid

    field = _parse_field(Vgrid.value, field)

    # start Displays
    Vtilt = Variable(0)
    plot1 = GridDisplay(Vgrid, Variable(field), Vtilt, name="Display",
                        parent=menu)

    menu.addLayoutWidget(plot1)

    menu.setGeometry(0, 0, 700, 700)

    # start program
    app.exec_()
