"""
core.py

Class instance to create Variables and establish change signals.
"""

# Load the needed packages
from PyQt4 import QtGui, QtCore

class Variable (QtCore.QObject):
    def __init__(self,value=None):
        """Class that holds a value, changing that with change() emits a signal"""
        QtCore.QObject.__init__(self)
        self.value=value

    def change (self,value):
        self.value=value
        self.emit(QtCore.SIGNAL("ValueChanged"),self,value)    


