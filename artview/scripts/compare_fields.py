"""
compare_fields.py

Driver function that creates ARTView display.
"""
import os
import sys

from ..core import Variable, QtGui, QtCore
from ..components import RadarDisplay, Menu, LinkPlugins
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field

def run(DirIn=None, filename=None, field=None):
    """
    artview execution for comparing fields in radar display
    """
    DirIn = _parse_dir(DirIn)

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    menu = Menu(DirIn, filename, mode="Radar", name="Menu")
    Vradar = menu.Vradar

    field = _parse_field(Vradar.value, field)

    # start Displays
    Vtilt = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display1",
                         parent=menu)
    plot2 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display2",
                         parent=menu)

    # start ComponentsControl
    control = LinkPlugins()

    # add control to Menu
    menu.addLayoutWidget(control)

    # add grafical starts
    _add_all_advanced_tools(menu)

    # start program
    app.exec_()
