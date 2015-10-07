"""
edit_radar.py

Driver function that creates an ARTView display for editing radar data.
Starts SelectRegion and Gatefilter.
"""
import artview
import os
import sys


def run(DirIn=None, filename=None, field=None):
    """
    artview execution for filtering gates radar display
    """
    DirIn = _parse_dir(DirIn)

    app = artview.core.QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
##menu = artview.components.Menu(os.getcwd(), None, mode="Radar", name="Menu")
    menu = artview.components.Menu(DirIn, filename, mode="Radar", name="Menu")
    Vradar = menu.Vradar

    # start Displays
    Vtilt = artview.core.Variable(0)
##plot1 = artview.components.RadarDisplay(
##    Vradar, artview.core.Variable("reflectivity"), Vtilt, name="Display",
##    parent=menu)
    plot1 = artview.components.RadarDisplay(
        Vradar, artview.core.Variable(field), Vtilt, name="Display",
        parent=menu)
    roi = artview.components.SelectRegion(plot1, 
                                          name="SelectRegion", parent=menu)

    filt =  artview.plugins.GateFilter(Vradar=Vradar, 
                                       Vgatefilter=plot1.Vgatefilter,
                                       name="GateFilter", parent=menu)
    menu.addLayoutWidget(roi)
    menu.addLayoutWidget(filt)
    roi.show()
    filt.show()

    menu.setGeometry(0, 0, 300, 300)

    # start program
    app.exec_()