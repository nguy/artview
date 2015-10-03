"""
standard.py

Driver function that creates ARTView display.
"""
import os


def run(DirIn=None, filename=None, field=None):
    """
    standard artview execution

    It has :py:class:`~artview.components.Menu`
    with :py:class:`~artview.components.LinkPlugins`,

    2 :py:class:`~artview.components.RadarDisplay`,

    graphical start for:
        * All :py:class:`~artview.plugins`
        * :py:class:`~artview.components.RadarDisplay`
        * :py:class:`~artview.components.LinkPlugins`
        * :py:class:`~artview.components.SelectRegion`
    """
    import sys

    from ..core import Variable, QtGui, QtCore
    from ..components import RadarDisplay, Menu, LevelButtonWindow, \
        LinkPlugins, SelectRegion
    from ._parse_field import _parse_field

    app = QtGui.QApplication(sys.argv)

    # start Menu and initiate Vradar
    MainMenu = Menu(DirIn, filename, name="Menu")
    Vradar = MainMenu.Vradar

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')
        field = _parse_field(Vradar.value, field)
    if DirIn is None:  # avoid reference to path while building documentation
        DirIn = os.getcwd()

    # start Displays
    Vtilt = Variable(0)
    Vtilt2 = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display1",
                         parent=MainMenu)
    plot2 = RadarDisplay(Vradar, Variable(field), Vtilt2, name="Display2",
                         parent=MainMenu)

    # start ComponentsControl
    control = LinkPlugins()

    # add control to Menu
    MainMenu.addLayoutWidget(control)

    # add grafical starts
    MainMenu.addComponent(LinkPlugins)
    MainMenu.addComponent(RadarDisplay)
    MainMenu.addComponent(SelectRegion)

    # add all plugins to grafical start
    try:
        from .. import plugins
        for plugin in plugins._plugins.values():
            MainMenu.addComponent(plugin)
    except:
        import warnings
        warnings.warn("Loading Plugins Fail")

    # Replace in Screen
    desktop_rect = QtGui.QDesktopWidget().screenGeometry()

    height = desktop_rect.height()
    width = desktop_rect.width()

    menu_width = 300
    menu_height = 180

    MainMenu.setGeometry(0, 0, menu_width, menu_height)

    plot_size = min(height-60-menu_height, width/2) - 50
    plot1.setGeometry(0, height-plot_size, plot_size, plot_size)
    plot2.setGeometry(width/2, height-plot_size, plot_size, plot_size)

    # start program
    app.exec_()
