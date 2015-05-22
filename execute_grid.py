"""
execute_two.py

Driver function that creates ARTView display.
"""
from PyQt4 import QtGui, QtCore
import sys

from core import Variable
from plot_grid import Display
from menu_grid import Menu
from tilt import TiltButtonWindow
#import .resources.plot as plot
#import .ui.menu as menu
import parser


DirIn,field=parser.parse(sys.argv)




app = QtGui.QApplication(sys.argv)

MainMenu = Menu(DirIn, name="Menu") #initiate Vradar
Vradar = MainMenu.Vradar
Vradar.value=None

Vtilt = Variable(0)
Vtilt2 = Variable(0)
plot1 = Display(Vradar, Variable(field), Vtilt, name="Display1", parent=MainMenu)


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

app.exec_()

