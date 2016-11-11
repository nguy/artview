"""
standard.py

Driver function that creates two ARTView displays.
This is the default start for ARTView
"""
import os
import sys

from ..core import Variable, QtGui, QtCore, componentsList
from ..components import RadarDisplay, Menu, LevelButtonWindow, \
    LinkSharedVariables, SelectRegion, Window, FileNavigator, \
    LayoutComponent
from ..plugins import FileDetail
from ._parse_field import _parse_field
from ._common import startMainMenu
from .. import view


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

    view.startWindow()

    if DirIn is None:  # avoid reference to path while building documentation
        DirIn = os.getcwd()

    menu = LayoutComponent(name="Menu")
    navigator = FileNavigator(DirIn, filename)

    menu.layout.addWidget(navigator, 0, 0)
    menu.layout.addWidget(FileDetail(Vradar=navigator.Vradar,
                                     Vgrid=navigator.Vgrid), 0, 1)
    menu.layout.setColumnStretch(2, 1)

    Vradar = navigator.Vradar

    # handle input
    if field is None:
        import pyart
        field = pyart.config.get_field_name('reflectivity')
        field = _parse_field(Vradar.value, field)

    # start Displays
    Vtilt = Variable(0)
    plot1 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display1",
                         parent=view.MainWindow)
    plot2 = RadarDisplay(Vradar, Variable(field), Vtilt, name="Display2",
                         parent=view.MainWindow)

    # start ComponentsControl
    control = LinkSharedVariables()
    control.setComponent0(plot1.name)
    control.setComponent1(plot2.name)

    # add control to Menu
    #view.MainMenu.addLayoutWidget(control)
    window = view.MainWindow
    window.splitHorizontal()
    window.splitVertical()

    window.layoutTree[(0,1,0)].addTab(control,control.name)
    window.layoutTree[(0,0)].addTab(menu,menu.name)
    window.layoutTree[(0,0)].tabBar().setVisible(False)
    window.layoutTree[(0,1,1)].addTab(plot1,plot1.name)
    window.layoutTree[(0,1,1)].addTab(plot2,plot2.name)

    window.layoutTree[(0,1,0)].fix=True
    window.layoutTree[(0,1,0)].setSizePolicy(0,0)
    window.layoutTree[(0,1,0)].sizePolicy().setHorizontalStretch(1)
    window.layoutTree[(0,1,0)].sizePolicy().setVerticalStretch(1)
    window.layoutTree[(0,1,1)].sizePolicy().setHorizontalStretch(3)
    window.layoutTree[(0,1,1)].sizePolicy().setVerticalStretch(3)

    window.showMaximized()
    geom =  QtGui.QDesktopWidget().screenGeometry()
    window.layoutTree[(0,)].setSizes([window.layoutTree[(0,0)].minimumSize().height(),geom.height()-window.layoutTree[(0,0)].minimumSize().height()])
    window.layoutTree[(0,1)].setSizes([window.layoutTree[(0,1,0)].minimumSize().width(),geom.width()-window.layoutTree[(0,1,0)].minimumSize().width()])

    # start program
    view.execute()
    print("You used ARTView. What you think and what you need of ARTView? "
          "Send your comment to artview-users@googlegroups.com")
