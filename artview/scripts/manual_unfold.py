"""
compare_fields.py

Driver function that creates ARTView display.
"""
import os
import sys

from ..core import Variable, QtGui, QtCore
from ..components import RadarDisplay, Menu, LinkSharedVariables, SelectRegion
from ._common import _add_all_advanced_tools, _parse_dir, _parse_field
from ..plugins import ManualUnfold


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for manual unfolding velocity field of radar
    """
    DirIn = _parse_dir(DirIn)

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    menu = Menu(DirIn, filename, mode=("Radar",), name="Menu")
    Vradar = menu.Vradar

    field = _parse_field(Vradar.value, field)

    # start Displays
    Vtilt = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display1",
                         parent=menu)
    plot2 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display2",
                         parent=menu)

    # connect zoom
    plot2.disconnectSharedVariable('Vlimits')
    plot2.Vlimits = plot1.Vlimits
    plot2.connectSharedVariable('Vlimits')

    # start region selection tool
    roi = SelectRegion(plot1, name="SelectRegion", parent=menu)

    # start unfold tool
    unfold = ManualUnfold(Vradar, roi.Vpoints, name=" ManualUnfold",
                          parent=menu)

    # start ComponentsControl
    control = LinkSharedVariables()

    # add components to Menu
    menu.addLayoutWidget(control)
    menu.addLayoutWidget(roi)
    menu.addLayoutWidget(unfold)
    control.show()
    roi.show()
    unfold.show()

    # Replace in Screen
    desktop_rect = QtGui.QDesktopWidget().screenGeometry()

    height = desktop_rect.height()
    width = desktop_rect.width()

    menu_width = 300
    menu_height = 180

    menu.setGeometry(0, 0, menu_width, menu_height)

    plot_size = min(height-60-menu_height, width/2) - 50
    plot1.setGeometry(0, height-plot_size, plot_size, plot_size)
    plot2.setGeometry(width/2, height-plot_size, plot_size, plot_size)

    # start program
    app.exec_()
