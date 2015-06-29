"""
map_to_grid.py

Driver function that creates ARTView display.
"""

def run(DirIn='./', filename=None, field=None):
    """artview execution"""
    print DirIn
    from PyQt4 import QtGui, QtCore
    import sys

    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')

    from ..core import Variable
    from ..components import Display, Display_grid, Menu, TiltButtonWindow, ComponentsControl

    app = QtGui.QApplication(sys.argv)

    MainMenu = Menu(DirIn, filename, name="Menu") #initiate Vradar
    Vradar = MainMenu.Vradar

    Vfield = Variable(field)
    plot = Display(Vradar, Vfield, Variable(0), name="DisplayRadar", parent=MainMenu)
    plot1 = Display_grid(Variable(None), Vfield, Variable(0), name="DisplayGrid", parent=MainMenu)
    from .. import plugins

    mapper = plugins.mapper(plot.Vradar, plot1.Vgrid, name="Mapper", parent=MainMenu)


    control = ComponentsControl()
    MainMenu.addLayoutWidget(control)
    MainMenu.addComponent(ComponentsControl)
    MainMenu.addComponent(Display)

    try:
        from .. import plugins
        for plugin in plugins._plugins:
            MainMenu.addComponent(plugin)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

    app.exec_()






