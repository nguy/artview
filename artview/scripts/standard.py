"""
standard.py

Driver function that creates ARTView display.
"""

def run(DirIn='./', filename=None, field=None):
    """
    standard artview execution
    
    It has :py:class:`~artview.components.Menu` with :py:class:`~artview.components.ComponentsControl`,

    2 :py:class:`~artview.components.Display`,

    grafical start for:
        * All :py:class:`~artview.plugins`
        * :py:class:`~artview.components.Display`
        * :py:class:`~artview.components.ComponentsControl`
    """
    from PyQt4 import QtGui, QtCore
    import sys

    from ..core import Variable
    from ..components import Display, Menu, TiltButtonWindow, ComponentsControl

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')

    # start pyqt
    app = QtGui.QApplication(sys.argv)

    # start Menu
    MainMenu = Menu(DirIn, filename, name="Menu") #initiate Vradar
    Vradar = MainMenu.Vradar

    # start Displays
    Vtilt = Variable(0)
    Vtilt2 = Variable(0)
    plot1 = Display(Vradar, Variable(field), Vtilt, name="Display1", parent=MainMenu)
    plot2 = Display(Vradar, Variable(field), Vtilt2, name="Display2", parent=MainMenu)

    # start ComponentsControl
    control = ComponentsControl()

    # add control to Menu
    MainMenu.addLayoutWidget(control)

    # add grafical starts
    MainMenu.addComponent(ComponentsControl)
    MainMenu.addComponent(Display)

    # add all plugins to grafical start
    try:
        from .. import plugins
        for plugin in plugins._plugins:
            MainMenu.addComponent(plugin)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

    # Replace in Screen
    desktop_rect = QtGui.QDesktopWidget().screenGeometry()

    height = desktop_rect.height()
    width = desktop_rect.width()

    menu_width = max(MainMenu.menubar.sizeHint().width(), MainMenu.sizeHint().width())
    menu_height = MainMenu.sizeHint().height()

    MainMenu.setGeometry(0,0,menu_width,menu_height)

    plot_size = min(height-60-menu_height, width/2)-50
    plot1.setGeometry(0,height-plot_size,plot_size,plot_size)
    plot2.setGeometry(width/2,height-plot_size,plot_size,plot_size)

    # start program
    app.exec_()

