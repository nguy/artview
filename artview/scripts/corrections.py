"""
corrections.py

Driver function that creates an ARTView display for
work with corrections routines.
"""
import os
import sys

from ..core import Variable, QtGui, QtCore
from ..components import RadarDisplay, Menu
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field
from ..plugins import (DealiasRegionBased, DealiasUnwrapPhase, PhaseProcLp,
                       CalculateAttenuation)

corrections = [DealiasRegionBased, DealiasUnwrapPhase, PhaseProcLp,
               CalculateAttenuation]


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for radar corrections
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

    menu.setGeometry(0, 0, 700, 700)

    for correction in corrections:
        c = correction(Vradar=Vradar, parent=menu)
        menu.addLayoutWidget(c)
        c.show()

    # start program
    app.exec_()
