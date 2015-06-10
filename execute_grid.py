"""
execute_two.py

Driver function that creates ARTView display.
"""
from PyQt4 import QtGui, QtCore
import sys

from core import Variable
from plot import Display
from plot_grid import Display as Display_grid
from menu import Menu
from tilt import TiltButtonWindow
#import .resources.plot as plot
#import .ui.menu as menu
import parser


DirIn,field=parser.parse(sys.argv)




app = QtGui.QApplication(sys.argv)

MainMenu = Menu(DirIn, name="Menu") #initiate Vradar
Vradar = MainMenu.Vradar


Vfield = Variable(field)
plot = Display(Vradar, Vfield, Variable(0), name="DisplayRadar", parent=MainMenu)
plot1 = Display_grid(Variable(None), Vfield, Variable(0), name="DisplayGrid", parent=MainMenu)


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

