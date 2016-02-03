"""
map_to_grid.py

Driver function that creates two ARTView displays,
the first for native coordinate radar data and the second for
gridded radar data. The Mapper tool is initiated.
"""
import os
import sys

from ..core import Variable,  QtGui, QtCore
from ..components import RadarDisplay, GridDisplay, Menu
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for mapping radar data to grid
    """
    DirIn = _parse_dir(DirIn)

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    menu = Menu(DirIn, filename, mode=("Radar",), name="Menu")
    Vradar = menu.Vradar

    field = _parse_field(Vradar.value, field)

    # start Displays
    plot1 = RadarDisplay(Vradar, Variable(field), Variable(0),
                         name="Radar", parent=menu)
    plot2 = GridDisplay(Variable(None), Variable(field), Variable(0),
                        name="Grid", parent=menu)

    # start Mapper
    from ..plugins import Mapper
    mapper = Mapper(plot1.Vradar, plot2.Vgrid, name="Mapper",
                    parent=menu)

    menu.addLayoutWidget(mapper)

    menu.setGeometry(0, 0, 600, 600)

    # start program
    app.exec_()
