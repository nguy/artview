"""

"""

# Load the needed packages
from PyQt4 import QtGui, QtCore
from functools import partial

import core
import common

class Exemple2(core.Component):
    @classmethod
    def guiStart(self, parent=None):
        val, entry = common.string_dialog("Exemple2", "Exemple2", "Name:")
        return self(name=val, parent=parent)

    def __init__(self, name="Exemple2", parent=None):
        '''Initialize the class to create the interface'''
        super(Exemple2, self).__init__(name=name, parent=parent)
        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtGui.QGridLayout(self.central_widget)
        
        self.layout.addWidget(QtGui.QLabel("Horizontal Plugin named: %s"%self.name), 0, 0)
        self.button = QtGui.QPushButton("Close")
        self.button .clicked.connect(self.close)
        self.layout.addWidget(self.button, 0, 1)
        self.show()

    def close(self):
        super(Exemple2, self).close()

_plugins=[Exemple2]
