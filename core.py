
from PyQt4 import QtGui, QtCore




VERSION = '0.1.6'
MAINWINDOWTITLE = 'ARTView - ARM Radar Toolkit Viewer'



class Variable (QtCore.QObject):
    def __init__(self,value=None):
        """class that holds a value, changing that with change() emits a signal"""
        QtCore.QObject.__init__(self)
        self.value=value

    def change (self,value):
        self.value=value
        self.emit(QtCore.SIGNAL("ValueChanged"),self,value)    


