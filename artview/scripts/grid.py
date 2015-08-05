"""
standard.py

Driver function that creates ARTView display.
"""
import os

def run(DirIn=os.getcwd(), filename=None, field=None):
    """
    standard artview execution

    It has :py:class:`~artview.components.Menu`
    with :py:class:`~artview.components.ComponentsControl`,

    2 :py:class:`~artview.components.Display`,

    graphical start for:
        * All :py:class:`~artview.plugins`
        * :py:class:`~artview.components.Display`
        * :py:class:`~artview.components.ComponentsControl`
    """
    from PyQt4 import QtGui, QtCore
    import sys

    from ..core import Variable
    from ..components import GridDisplay, Menu, LevelButtonWindow, \
        ComponentsControl, ROI

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    MainMenu = Menu(DirIn, filename, mode="Grid", name="Menu")
    Vgrid = MainMenu.Vgrid

    # start Displays
    Vtilt = Variable(0)
    Vfield = Variable(field)
    plot1 = GridDisplay(Vgrid, Vfield, Vtilt, name="Display1",
                    parent=MainMenu)
    plot2 = GridDisplay(Vgrid, Vfield, Vtilt, name="DisplayLat", plot_type="gridY",
                    parent=MainMenu)
    plot3 = GridDisplay(Vgrid, Vfield, Vtilt, name="DisplayLon", plot_type="gridX",
                    parent=MainMenu)

    # start ComponentsControl
    control = ComponentsControl()

    # add control to Menu
    MainMenu.addLayoutWidget(control)

    # add grafical starts
    MainMenu.addComponent(ComponentsControl)
    MainMenu.addComponent(GridDisplay)
    MainMenu.addComponent(ROI)

    # add all plugins to grafical start
    try:
        from .. import plugins
        for plugin in plugins._plugins:
            MainMenu.addComponent(plugin)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

    # start program
    app.exec_()
