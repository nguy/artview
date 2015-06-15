"""
execute_two.py

Driver function that creates ARTView display.
"""
from PyQt4 import QtGui, QtCore
import sys

from core import Variable
from plot import Display
from menu import Menu
from tilt import TiltButtonWindow
#import .resources.plot as plot
#import .ui.menu as menu
import parser


DirIn,field=parser.parse(sys.argv)




app = QtGui.QApplication(sys.argv)

MainMenu = Menu(DirIn, name="Menu") #initiate Vradar
Vradar = MainMenu.Vradar

Vtilt = Variable(0)
Vtilt2 = Variable(0)
plot1 = Display(Vradar, Variable(field), Vtilt, name="Display1", parent=MainMenu)
plot2 = Display(Vradar, Variable(field), Vtilt2, name="Display2", parent=MainMenu)

from component_control import ComponentsControl

c = ComponentsControl()
MainMenu.addLayoutWidget(c)
MainMenu.addComponent(ComponentsControl)

try:
    import plugins
    for plugin in plugins._plugins:
        MainMenu.addComponent(plugin)
except:
    import warnings
    warnings.warn("Loading Plugins Fail")

desktop_rect = QtGui.QDesktopWidget().screenGeometry()

height = desktop_rect.height()
width = desktop_rect.width()

menu_width = max(MainMenu.menubar.sizeHint().width(), MainMenu.sizeHint().width())
menu_height = MainMenu.sizeHint().height()

MainMenu.setGeometry(0,0,menu_width,menu_height)

plot_size = min(height-60-menu_height, width/2)-50
plot1.setGeometry(0,height-plot_size,plot_size,plot_size)
plot2.setGeometry(width/2,height-plot_size,plot_size,plot_size)


app.exec_()

