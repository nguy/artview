"""
map_to_grid.py

Driver function that creates ARTview display.
"""
import os

def run(DirIn=os.getcwd(), filename=None, field=None):
    """
    ARTview execution to pyart mapping display.

    It has :py:class:`~artview.components.Menu`
    with :py:class:`~artview.components.LinkDisplay`,
    menu is opening radar files

    1 radar and 1 grid sharing Vfield

    :py:class:`~artview.plugins.Mapper` connected to both displays

    graphical start for:
        * All :py:class:`~artview.plugins`
        * :py:class:`~artview.components.RadarDisplay`
        * :py:class:`~artview.components.LinkDisplay`

    """
    from PyQt4 import QtGui, QtCore
    import sys

    from ..core import Variable
    from ..components import RadarDisplay, GridDisplay, Menu, LevelButtonWindow, \
        LinkDisplay

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')

    # start pyqt
    app = QtGui.QApplication(sys.argv)

    # start Menu
    MainMenu = Menu(DirIn, filename, mode="Radar", name="Menu")
    # initiate Vradar
    Vradar = MainMenu.Vradar

    # start Displays
    Vfield = Variable(field)
    plot = RadarDisplay(Vradar, Vfield, Variable(0), name="DisplayRadar",
                   parent=MainMenu)
    plot1 = GridDisplay(Variable(None), Vfield, Variable(0),
                         name="DisplayGrid", parent=MainMenu)

    # start Mapper
    from .. import plugins
    mapper = plugins.Mapper(plot.Vradar, plot1.Vgrid, name="Mapper",
                            parent=MainMenu)

    # start LinkDisplay
    control = LinkDisplay()

    # add control to Menu
    MainMenu.addLayoutWidget(control)

    # add grafical starts
    MainMenu.addComponent(LinkDisplay)
    MainMenu.addComponent(RadarDisplay)

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
