"""
standard.py

Driver function that creates two ARTView displays.
This is the default start for ARTView
"""
import os


def run(DirIn=None, filename=None, field=None):
    """
    standard artview execution

    It has :py:class:`~artview.components.Menu`
    with :py:class:`~artview.components.LinkSharedVariables`,

    2 :py:class:`~artview.components.RadarDisplay`,

    graphical start for:
        * All :py:class:`~artview.plugins`
        * :py:class:`~artview.components.RadarDisplay`
        * :py:class:`~artview.components.LinkSharedVariables`
        * :py:class:`~artview.components.SelectRegion`
    """
    import sys

    from ..core import Variable, QtGui, QtCore
    from ..components import RadarDisplay, Menu, LevelButtonWindow, \
        LinkSharedVariables, SelectRegion
    from ._parse_field import _parse_field
    from ._common import startMainMenu
    from .. import view

    view.start(DirIn, filename)
    Vradar = view.MainMenu.Vradar

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')
        field = _parse_field(Vradar.value, field)
    if DirIn is None:  # avoid reference to path while building documentation
        DirIn = os.getcwd()

    # start Displays
    Vtilt = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display1",
                         parent=view.MainMenu)
    plot2 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display2",
                         parent=view.MainMenu)

    # start ComponentsControl
    control = LinkSharedVariables()
    control.setComponent0(plot1.name)
    control.setComponent1(plot2.name)

    # add control to Menu
    view.MainMenu.addLayoutWidget(control)

    # Replace in Screen
    desktop_rect = QtGui.QDesktopWidget().screenGeometry()

    height = desktop_rect.height()
    width = desktop_rect.width()

    menu_width = 500
    menu_height = 180

    view.MainMenu.setGeometry(0, 0, menu_width, menu_height)

    plot_size = min(height-60-menu_height, width/2) - 50
    plot1.setGeometry(0, height-plot_size, plot_size, plot_size)
    plot2.setGeometry(width/2, height-plot_size, plot_size, plot_size)

    # start program
    view.execute()
    print("You used ARTView. What you think and what you need of ARTView? "
          "Send your comment to artview-users@googlegroups.com")
