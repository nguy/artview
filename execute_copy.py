
from PyQt4 import QtGui, QtCore
import sys

from core import Variable
import plot
import menu
import parser


DirIn,field=parser.parse(sys.argv)

Vradar = Variable(None)


app = QtGui.QApplication(sys.argv)

MainMenu=menu.Menu(Vradar,DirIn,name="Menu") #initiate Vradar

Vtilt=Variable(0)
plot1=plot.Display(Vradar,Variable(field),Vtilt,name="Display1",parent=MainMenu)
plot2=plot.Display(Vradar,Variable(field),Vtilt,name="Display2",parent=MainMenu)


app.exec_()
