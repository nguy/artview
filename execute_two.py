
from PyQt4 import QtGui, QtCore
import sys

from core import Variable
from plot import Display
from menu import Menu
from tilt import TiltButtonWindow
#import .resources.plot as plot
#import .ui.menu as menu
import parser


class make_MainDisplay(object):
    '''Make a class to hold the display objects'''
    def __init__(self, menu, plots=None):
       self.menu = menu
       self.plot1 = plots[0]
       self.plot2 = plots[1]

DirIn,field=parser.parse(sys.argv)

Vradar = Variable(None)


app = QtGui.QApplication(sys.argv)

MainMenu = Menu(Vradar, DirIn, name="Menu") #initiate Vradar

Vtilt = Variable(0)
Vtilt2 = Variable(0)
Vlims = Variable(None)
plot1 = Display(Vradar, Variable(field), Vtilt, Vlims, name="Display1", parent=MainMenu)
plot2 = Display(Vradar, Variable(field), Vtilt2, Vlims, name="Display2", parent=MainMenu)
#tiltselect = TiltButtonWindow(Vradar, Variable(0), name="Tilt Selection", parent=MainMenu)

#MainDisplay = make_MainDisplay(MainMenu, plots=[plot1, plot2])


#MainMenu=menu.Menu(Vradar,DirIn,name="Menu") #initiate Vradar

#plot1=plot.Display(Vradar,Variable(field),Variable(0),name="Display1",parent=MainMenu)
#plot2=plot.Display(Vradar,Variable(field),Variable(0),name="Display2",parent=MainMenu)


app.exec_()
