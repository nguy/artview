"""
select_region.py

Driver function that creates an ARTView display and initiates
the SelectRegion tool.
"""
import os
import sys

from ..core import Variable, QtGui, QtCore
from ..components import RadarDisplay, Menu, SelectRegion, PlotDisplay
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for selecting a region in radar display
    """
    DirIn = _parse_dir(DirIn)

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    menu = Menu(DirIn, filename, mode=("Radar",), name="Menu")
    Vradar = menu.Vradar

    field = _parse_field(Vradar.value, field)

    # start Displays
    Vtilt = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display",
                         parent=menu)
    roi = SelectRegion(VplotAxes=plot1.VplotAxes,
                       VpathInteriorFunc=plot1.VpathInteriorFunc,
                       Vfield=plot1.Vfield,
                       name="SelectRegion", parent=menu)

    menu.addLayoutWidget(roi)

    menu.setGeometry(0, 0, 300, 300)

    # start program
    app.exec_()
