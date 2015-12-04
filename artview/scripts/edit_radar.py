"""
edit_radar.py

Driver function that creates an ARTView display for editing radar data.
Starts SelectRegion and Gatefilter.
"""
import os
import sys

from ..core import Variable, QtGui
from ..components import RadarDisplay, Menu, SelectRegion
from ..plugins import GateFilter
from ._common import _parse_dir, _parse_field


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for filtering gates radar display
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
    roi = SelectRegion(plot1, name="SelectRegion", parent=menu)

    filt = GateFilter(Vradar=Vradar, Vgatefilter=plot1.Vgatefilter,
                      name="GateFilter", parent=menu)
    menu.addLayoutWidget(roi)
    menu.addLayoutWidget(filt)
    roi.show()
    filt.show()

    menu.setGeometry(0, 0, 300, 300)

    # start program
    app.exec_()
