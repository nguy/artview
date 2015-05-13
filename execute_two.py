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
app.exec_()

