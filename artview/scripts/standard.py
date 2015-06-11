"""
execute.py

Driver function that creates ARTView display.
"""

def run(DirIn='./', field='reflectivity'):
    """standard artview execution"""
    print DirIn
    from PyQt4 import QtGui, QtCore
    import sys

    from ..core import Variable
    from ..components import Display, Menu, TiltButtonWindow, ComponentsControl

    app = QtGui.QApplication(sys.argv)

    MainMenu = Menu(DirIn, name="Menu") #initiate Vradar
    Vradar = MainMenu.Vradar

    Vtilt = Variable(0)
    Vtilt2 = Variable(0)
    plot1 = Display(Vradar, Variable(field), Vtilt, name="Display1", parent=MainMenu)
    plot2 = Display(Vradar, Variable(field), Vtilt2, name="Display2", parent=MainMenu)

    control = ComponentsControl()
    MainMenu.addLayoutWidget(control)
    MainMenu.addComponent(ComponentsControl)

    try:
        from .. import plugins
        for plugin in plugins._plugins:
            MainMenu.addComponent(plugin)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

    app.exec_()

